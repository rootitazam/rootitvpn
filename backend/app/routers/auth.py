from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Admin
from app.schemas import AdminLogin, AdminResponse
from app.utils.crypto import hash_password, verify_password
from app.config import settings
from starlette.requests import Request
from starlette.responses import Response
import secrets

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBasic()


def get_current_admin(request: Request, db: Session = Depends(get_db)) -> Admin:
    """Get current admin from session"""
    admin_id = request.session.get("admin_id")
    if not admin_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin not found"
        )
    
    return admin


def init_admin_user(db: Session):
    """Initialize admin user if not exists"""
    admin = db.query(Admin).filter(Admin.username == settings.admin_username).first()
    if not admin:
        admin = Admin(
            username=settings.admin_username,
            password_hash=hash_password(settings.admin_password)
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin
    return admin


@router.post("/login", response_model=AdminResponse)
async def login(
    credentials: AdminLogin,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Admin login with session-based authentication"""
    # Initialize admin if not exists
    init_admin_user(db)
    
    admin = db.query(Admin).filter(Admin.username == credentials.username).first()
    
    if not admin or not verify_password(credentials.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Create session
    request.session["admin_id"] = admin.id
    request.session["admin_username"] = admin.username
    
    # Update last login
    from datetime import datetime
    admin.last_login = datetime.utcnow()
    db.commit()
    
    return AdminResponse(
        id=admin.id,
        username=admin.username,
        created_at=admin.created_at,
        last_login=admin.last_login
    )


@router.post("/logout")
async def logout(request: Request):
    """Logout and clear session"""
    request.session.clear()
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=AdminResponse)
async def get_current_user(
    admin: Admin = Depends(get_current_admin)
):
    """Get current admin info"""
    return AdminResponse(
        id=admin.id,
        username=admin.username,
        created_at=admin.created_at,
        last_login=admin.last_login
    )


@router.get("/check")
async def check_auth(admin: Admin = Depends(get_current_admin)):
    """Check if user is authenticated"""
    return {"authenticated": True, "username": admin.username}

