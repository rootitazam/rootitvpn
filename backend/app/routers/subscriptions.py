from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import SubscriptionResponse
from app.routers.auth import get_current_admin
from app.models import Admin
from app.services.subscription_service import SubscriptionService
from app.services.reality_service import RealityService
from app.config import settings

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


def get_subscription_service(db: Session) -> SubscriptionService:
    """Get subscription service instance"""
    reality_service = RealityService(db)
    return SubscriptionService(reality_service)


@router.get("/{user_id}", response_model=SubscriptionResponse)
async def get_user_subscription(
    user_id: str,
    server_ip: str = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Get subscription links for a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Use provided server IP or from config
    from app.config import settings
    if not server_ip:
        server_ip = settings.server_ip or None  # Will use default from service
    
    subscription_service = get_subscription_service(db)
    return subscription_service.generate_subscription_response(user, server_ip)


@router.get("/{user_id}/v2rayng")
async def get_v2rayng_link(
    user_id: str,
    server_ip: str = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Get v2rayNG subscription link"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    from app.config import settings
    if not server_ip:
        server_ip = settings.server_ip or None
    
    subscription_service = get_subscription_service(db)
    links = subscription_service.generate_subscription_links(user, server_ip)
    return {"link": links["v2rayng"]}


@router.get("/{user_id}/shadowrocket")
async def get_shadowrocket_link(
    user_id: str,
    server_ip: str = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Get Shadowrocket subscription link"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    from app.config import settings
    if not server_ip:
        server_ip = settings.server_ip or None
    
    subscription_service = get_subscription_service(db)
    links = subscription_service.generate_subscription_links(user, server_ip)
    return {"link": links["shadowrocket"]}


@router.get("/{user_id}/nekoray")
async def get_nekoray_link(
    user_id: str,
    server_ip: str = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Get Nekoray subscription link"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    from app.config import settings
    if not server_ip:
        server_ip = settings.server_ip or None
    
    subscription_service = get_subscription_service(db)
    links = subscription_service.generate_subscription_links(user, server_ip)
    return {"link": links["nekoray"]}

