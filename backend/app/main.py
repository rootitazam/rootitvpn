from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.sessions import SessionMiddleware
from app.config import settings
from app.database import init_db
from app.routers import auth, users, monitoring, subscriptions, xray
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.utils.log_rotation import rotate_logs, clean_access_logs_db
from app.database import SessionLocal
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="RootitVPN API",
    description="VPN Management Panel API for Xray-core",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    max_age=3600 * 24,  # 24 hours
    same_site="lax"
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.debug else "An error occurred"
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body}
    )

# Initialize database
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database...")
    init_db()
    
    # Initialize admin user
    from app.routers.auth import init_admin_user
    db = SessionLocal()
    try:
        init_admin_user(db)
        logger.info("Admin user initialized")
    finally:
        db.close()
    
    # Initialize Xray config if it doesn't exist
    from app.services.reality_service import RealityService
    from app.services.routing_service import RoutingService
    from app.services.xray_service import XrayService
    from app.models import User
    from pathlib import Path
    
    config_path = Path(settings.xray_config_path)
    db = SessionLocal()
    try:
        reality_service = RealityService(db)
        config = reality_service.get_or_create_config()
        
        # Set server_ip from settings if not in database
        if not config.server_ip and settings.server_ip:
            reality_service.update_server_ip(settings.server_ip)
            logger.info(f"Server IP initialized from settings: {settings.server_ip}")
        
        # Generate Reality settings if not exists
        if not reality_service.get_current_settings().get("public_key"):
            reality_service.rotate_reality_settings()
        
        # Always regenerate Xray config to ensure it has latest Reality settings
        routing_service = RoutingService()
        xray_service = XrayService(reality_service, routing_service)
        
        users = db.query(User).filter(User.is_active == True).all()
        xray_config = xray_service.generate_config(users)
        if xray_service.save_config(xray_config):
            logger.info("Xray config generated/updated successfully")
        else:
            logger.error("Failed to generate/update Xray config")
    except Exception as e:
        logger.error(f"Error initializing config: {e}")
    finally:
        db.close()
    
    # Start scheduler for log rotation
    scheduler = AsyncIOScheduler()
    
    # Schedule log rotation every hour
    scheduler.add_job(
        rotate_logs,
        "interval",
        hours=1,
        id="log_rotation",
        replace_existing=True
    )
    
    # Schedule database log cleanup every 6 hours
    def cleanup_db_logs():
        db = SessionLocal()
        try:
            clean_access_logs_db(db)
        finally:
            db.close()
    
    scheduler.add_job(
        cleanup_db_logs,
        "interval",
        hours=6,
        id="db_log_cleanup",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started for log rotation")
    
    # Schedule Reality settings rotation
    from app.services.reality_service import RealityService
    def rotate_reality():
        db = SessionLocal()
        try:
            reality_service = RealityService(db)
            reality_service.rotate_reality_settings()
        finally:
            db.close()
    
    scheduler.add_job(
        rotate_reality,
        "interval",
        hours=settings.reality_rotation_hours,
        id="reality_rotation",
        replace_existing=True
    )
    
    # Schedule stats sync from Xray
    from app.services.stats_service import StatsService
    def sync_stats():
        db = SessionLocal()
        try:
            stats_service = StatsService(db)
            updated = stats_service.sync_all_users_stats()
            logger.info(f"Synced stats for {updated} users")
        except Exception as e:
            logger.error(f"Error syncing stats: {e}")
        finally:
            db.close()
            if 'stats_service' in locals():
                stats_service.close()
    
    scheduler.add_job(
        sync_stats,
        "interval",
        minutes=5,  # Sync every 5 minutes
        id="stats_sync",
        replace_existing=True
    )
    
    logger.info("Application started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down...")


# Include routers
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(users.router, prefix=settings.api_v1_prefix)
app.include_router(monitoring.router, prefix=settings.api_v1_prefix)
app.include_router(subscriptions.router, prefix=settings.api_v1_prefix)
app.include_router(xray.router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    return {
        "message": "RootitVPN API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "database": "unknown",
        "xray": "unknown"
    }
    
    # Check database
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Xray gRPC
    try:
        from app.services.xray_grpc_client import XrayGRPCClient
        client = XrayGRPCClient()
        if client.channel:
            health_status["xray"] = "connected"
        else:
            health_status["xray"] = "disconnected"
            health_status["status"] = "degraded"
        client.close()
    except Exception as e:
        health_status["xray"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return health_status

