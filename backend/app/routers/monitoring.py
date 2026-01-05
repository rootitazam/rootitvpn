from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, Device, AccessLog
from app.schemas import OnlineUser, MonitoringStats, DeviceResponse, AccessLogResponse
from app.routers.auth import get_current_admin
from app.models import Admin
from datetime import datetime, timedelta
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except:
                pass


manager = ConnectionManager()


@router.get("/online-users", response_model=List[OnlineUser])
async def get_online_users(
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Get list of online users"""
    from app.services.stats_service import StatsService
    
    try:
        stats_service = StatsService(db)
        online_user_uuids = stats_service.get_online_users()
        
        # Get users from database
        online_users_list = []
        if online_user_uuids:
            users = db.query(User).filter(
                User.uuid.in_(online_user_uuids),
                User.is_active == True
            ).all()
            
            for user in users:
                # Get real-time stats
                traffic = stats_service.get_user_traffic(user.uuid)
                user.data_used = traffic.get('total', user.data_used)
                
                # Get devices
                devices = db.query(Device).filter(Device.user_id == user.id).all()
                last_seen = datetime.utcnow()  # Approximate from stats
                if devices:
                    last_seen = max([d.last_seen for d in devices], default=datetime.utcnow())
                
                online_users_list.append(OnlineUser(
                    user_id=user.id,
                    username=user.username,
                    uuid=user.uuid,
                    data_used=user.data_used,
                    data_limit=user.data_limit,
                    last_seen=last_seen,
                    devices=[DeviceResponse(
                        id=d.id,
                        fingerprint=d.fingerprint,
                        user_agent=d.user_agent,
                        last_seen=d.last_seen,
                        created_at=d.created_at
                    ) for d in devices]
                ))
        
        stats_service.close()
        return online_users_list
    except Exception as e:
        logger.error(f"Error getting online users: {e}")
        # Fallback to device-based method
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)
        online_users_list = []
        users = db.query(User).filter(User.is_active == True).all()
        
        for user in users:
            recent_device = db.query(Device).filter(
                Device.user_id == user.id,
                Device.last_seen >= cutoff_time
            ).first()
            
            if recent_device:
                devices = db.query(Device).filter(Device.user_id == user.id).all()
                online_users_list.append(OnlineUser(
                    user_id=user.id,
                    username=user.username,
                    uuid=user.uuid,
                    data_used=user.data_used,
                    data_limit=user.data_limit,
                    last_seen=recent_device.last_seen,
                    devices=[DeviceResponse(
                        id=d.id,
                        fingerprint=d.fingerprint,
                        user_agent=d.user_agent,
                        last_seen=d.last_seen,
                        created_at=d.created_at
                    ) for d in devices]
                ))
        
        return online_users_list


@router.get("/stats", response_model=MonitoringStats)
async def get_monitoring_stats(
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Get monitoring statistics"""
    online_users = await get_online_users(db, admin)
    
    # Calculate 24h traffic
    cutoff_time = datetime.utcnow() - timedelta(hours=24)
    result = db.query(
        db.func.sum(AccessLog.bytes_sent + AccessLog.bytes_received).label("total")
    ).filter(AccessLog.timestamp >= cutoff_time).first()
    
    total_traffic_24h = result.total or 0
    
    return MonitoringStats(
        online_users=online_users,
        total_online=len(online_users),
        total_traffic_24h=total_traffic_24h
    )


@router.get("/devices", response_model=List[DeviceResponse])
async def get_devices(
    user_id: str = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Get device fingerprints"""
    query = db.query(Device)
    if user_id:
        query = query.filter(Device.user_id == user_id)
    
    devices = query.order_by(Device.last_seen.desc()).all()
    return devices


@router.get("/access-logs", response_model=List[AccessLogResponse])
async def get_access_logs(
    user_id: str = None,
    domain: str = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Get access logs (SNI logging)"""
    query = db.query(AccessLog)
    
    if user_id:
        query = query.filter(AccessLog.user_id == user_id)
    if domain:
        query = query.filter(AccessLog.domain.contains(domain))
    
    logs = query.order_by(AccessLog.timestamp.desc()).limit(limit).all()
    return logs


@router.get("/top-domains")
async def get_top_domains(
    limit: int = 20,
    hours: int = 24,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Get top visited domains"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    result = db.query(
        AccessLog.domain,
        db.func.count(AccessLog.id).label("count"),
        db.func.sum(AccessLog.bytes_sent + AccessLog.bytes_received).label("traffic")
    ).filter(
        AccessLog.timestamp >= cutoff_time,
        AccessLog.domain.isnot(None)
    ).group_by(AccessLog.domain).order_by(
        db.func.count(AccessLog.id).desc()
    ).limit(limit).all()
    
    return [
        {
            "domain": r.domain,
            "visits": r.count,
            "traffic": r.traffic or 0
        }
        for r in result
    ]


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time monitoring"""
    await manager.connect(websocket)
    try:
        while True:
            # Send updates every 5 seconds
            await asyncio.sleep(5)
            
            # Get fresh data (would need db session in production)
            # For now, send heartbeat
            await websocket.send_json({
                "type": "heartbeat",
                "timestamp": datetime.utcnow().isoformat()
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)

