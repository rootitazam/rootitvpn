from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    data_limit: int = 0  # 0 = unlimited
    expire_date: Optional[datetime] = None
    is_active: bool = True


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    data_limit: Optional[int] = None
    expire_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: str
    uuid: str
    data_used: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserStats(BaseModel):
    total_users: int
    active_users: int
    online_users: int
    total_data_used: int
    total_data_limit: int


# Device Schemas
class DeviceResponse(BaseModel):
    id: str
    fingerprint: str
    user_agent: Optional[str]
    last_seen: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


# Access Log Schemas
class AccessLogResponse(BaseModel):
    id: str
    user_id: str
    domain: Optional[str]
    bytes_sent: int
    bytes_received: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


class AccessLogStats(BaseModel):
    total_domains: int
    top_domains: List[dict]
    total_traffic: int


# Admin Schemas
class AdminLogin(BaseModel):
    username: str
    password: str


class AdminResponse(BaseModel):
    id: str
    username: str
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


# Monitoring Schemas
class OnlineUser(BaseModel):
    user_id: str
    username: str
    uuid: str
    data_used: int
    data_limit: int
    last_seen: datetime
    devices: List[DeviceResponse]


class MonitoringStats(BaseModel):
    online_users: List[OnlineUser]
    total_online: int
    total_traffic_24h: int


# Subscription Schemas
class SubscriptionResponse(BaseModel):
    v2rayng: str
    shadowrocket: str
    nekoray: str
    qr_code: str  # Base64 encoded QR code


# Xray Config Schemas
class XrayConfigResponse(BaseModel):
    id: str
    reality_dest: Optional[str]
    reality_public_key: Optional[str]
    reality_short_ids: Optional[List[str]]
    reality_server_names: Optional[List[str]]
    server_ip: Optional[str]
    last_rotated: Optional[datetime]
    updated_at: datetime
    
    class Config:
        from_attributes = True


class XrayConfigUpdate(BaseModel):
    reality_dest: Optional[str] = None
    reality_server_names: Optional[List[str]] = None
    server_ip: Optional[str] = None

