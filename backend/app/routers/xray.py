from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import XrayConfig, User
from app.schemas import XrayConfigResponse, XrayConfigUpdate
from app.routers.auth import get_current_admin
from app.models import Admin
from app.services.reality_service import RealityService
from app.services.routing_service import RoutingService
from app.services.xray_service import XrayService

router = APIRouter(prefix="/xray", tags=["Xray"])


def get_services(db: Session):
    """Get service instances"""
    reality_service = RealityService(db)
    routing_service = RoutingService()
    xray_service = XrayService(reality_service, routing_service)
    return xray_service, reality_service


@router.get("/config", response_model=XrayConfigResponse)
async def get_xray_config(
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Get current Xray configuration"""
    reality_service = RealityService(db)
    config = reality_service.get_or_create_config()
    
    return XrayConfigResponse(
        id=config.id,
        reality_dest=config.reality_dest,
        reality_public_key=config.reality_public_key,
        reality_short_ids=config.reality_short_ids,
        reality_server_names=config.reality_server_names,
        server_ip=config.server_ip,
        last_rotated=config.last_rotated,
        updated_at=config.updated_at
    )


@router.post("/config/rotate")
async def rotate_reality_settings(
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Manually rotate Reality settings"""
    reality_service = RealityService(db)
    config = reality_service.rotate_reality_settings()
    
    # Regenerate Xray config
    xray_service, _ = get_services(db)
    users = db.query(User).filter(User.is_active == True).all()
    xray_config = xray_service.generate_config(users)
    xray_service.save_config(xray_config)
    
    return {"message": "Reality settings rotated successfully", "config": XrayConfigResponse(
        id=config.id,
        reality_dest=config.reality_dest,
        reality_public_key=config.reality_public_key,
        reality_short_ids=config.reality_short_ids,
        reality_server_names=config.reality_server_names,
        server_ip=config.server_ip,
        last_rotated=config.last_rotated,
        updated_at=config.updated_at
    )}


@router.put("/config", response_model=XrayConfigResponse)
async def update_xray_config(
    config_update: XrayConfigUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Update Xray configuration"""
    reality_service = RealityService(db)
    
    if config_update.reality_dest:
        reality_service.update_dest(config_update.reality_dest)
    
    if config_update.reality_server_names:
        reality_service.update_server_names(config_update.reality_server_names)
    
    if config_update.server_ip is not None:
        reality_service.update_server_ip(config_update.server_ip)
    
    config = reality_service.get_or_create_config()
    
    # Regenerate Xray config
    xray_service, _ = get_services(db)
    users = db.query(User).filter(User.is_active == True).all()
    xray_config = xray_service.generate_config(users)
    xray_service.save_config(xray_config)
    
    return XrayConfigResponse(
        id=config.id,
        reality_dest=config.reality_dest,
        reality_public_key=config.reality_public_key,
        reality_short_ids=config.reality_short_ids,
        reality_server_names=config.reality_server_names,
        server_ip=config.server_ip,
        last_rotated=config.last_rotated,
        updated_at=config.updated_at
    )


@router.post("/reload")
async def reload_xray_config(
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Reload Xray configuration"""
    xray_service, _ = get_services(db)
    success = xray_service.reload_config()
    
    if success:
        return {"message": "Xray config reloaded successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reload Xray config"
        )


@router.get("/status")
async def get_xray_status(
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Get Xray service status"""
    try:
        from app.services.xray_grpc_client import XrayGRPCClient
        client = XrayGRPCClient()
        
        status = {
            "connected": client.channel is not None,
            "address": client.address,
            "config_exists": False
        }
        
        # Check if config file exists
        from pathlib import Path
        from app.config import settings
        config_path = Path(settings.xray_config_path)
        status["config_exists"] = config_path.exists()
        
        client.close()
        return status
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking Xray status: {str(e)}"
        )

