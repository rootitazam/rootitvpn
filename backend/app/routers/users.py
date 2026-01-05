from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserUpdate, UserResponse, UserStats
from app.routers.auth import get_current_admin
from app.models import Admin
from app.services.xray_service import XrayService
from app.services.reality_service import RealityService
from app.services.routing_service import RoutingService
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


def get_services(db: Session):
    """Get service instances"""
    reality_service = RealityService(db)
    routing_service = RoutingService()
    xray_service = XrayService(reality_service, routing_service)
    return xray_service, reality_service


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Get all users with pagination"""
    query = db.query(User)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return users


@router.get("/stats", response_model=UserStats)
async def get_user_stats(
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Get user statistics"""
    from app.services.stats_service import StatsService
    
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    # Get online users from Xray stats
    try:
        stats_service = StatsService(db)
        online_user_uuids = stats_service.get_online_users()
        online_users = len(online_user_uuids) if online_user_uuids else 0
        stats_service.close()
    except Exception as e:
        logger.error(f"Error getting online users count: {e}")
        online_users = 0
    
    # Data usage
    result = db.query(
        db.func.sum(User.data_used).label("total_used"),
        db.func.sum(User.data_limit).label("total_limit")
    ).first()
    
    total_data_used = result.total_used or 0
    total_data_limit = result.total_limit or 0
    
    return UserStats(
        total_users=total_users,
        active_users=active_users,
        online_users=online_users,
        total_data_used=total_data_used,
        total_data_limit=total_data_limit
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Create new user"""
    # Check if username exists
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Create user
    user = User(
        username=user_data.username,
        email=user_data.email,
        data_limit=user_data.data_limit,
        expire_date=user_data.expire_date,
        is_active=user_data.is_active,
        uuid=str(uuid.uuid4())
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Update Xray config
    xray_service, _ = get_services(db)
    users = db.query(User).filter(User.is_active == True).all()
    config = xray_service.generate_config(users)
    xray_service.save_config(config)
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Update user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    if user_data.username is not None:
        # Check if new username exists
        existing = db.query(User).filter(
            User.username == user_data.username,
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        user.username = user_data.username
    
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.data_limit is not None:
        user.data_limit = user_data.data_limit
    if user_data.expire_date is not None:
        user.expire_date = user_data.expire_date
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    # Update Xray config
    xray_service, _ = get_services(db)
    users = db.query(User).filter(User.is_active == True).all()
    config = xray_service.generate_config(users)
    xray_service.save_config(config)
    
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Delete user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    
    # Update Xray config
    xray_service, _ = get_services(db)
    users = db.query(User).filter(User.is_active == True).all()
    config = xray_service.generate_config(users)
    xray_service.save_config(config)
    
    return None


@router.post("/{user_id}/reset-data", response_model=UserResponse)
async def reset_user_data(
    user_id: str,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Reset user data usage"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.data_used = 0
    db.commit()
    db.refresh(user)
    
    return user

