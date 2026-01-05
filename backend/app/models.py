from sqlalchemy import Column, String, Integer, BigInteger, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=True)
    password_hash = Column(String, nullable=True)  # For future use if needed
    uuid = Column(String, unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))
    data_limit = Column(BigInteger, default=0)  # 0 = unlimited
    data_used = Column(BigInteger, default=0)
    expire_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    devices = relationship("Device", back_populates="user", cascade="all, delete-orphan")
    access_logs = relationship("AccessLog", back_populates="user", cascade="all, delete-orphan")


class Device(Base):
    __tablename__ = "devices"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    fingerprint = Column(String, nullable=False, index=True)
    user_agent = Column(String, nullable=True)
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="devices")


class AccessLog(Base):
    __tablename__ = "access_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    domain = Column(String, nullable=True, index=True)  # SNI
    bytes_sent = Column(BigInteger, default=0)
    bytes_received = Column(BigInteger, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="access_logs")


class XrayConfig(Base):
    __tablename__ = "xray_config"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    current_config_json = Column(Text, nullable=True)
    reality_dest = Column(String, nullable=True)
    reality_private_key = Column(String, nullable=True)
    reality_public_key = Column(String, nullable=True)
    reality_short_ids = Column(JSON, nullable=True)  # List of short IDs
    reality_server_names = Column(JSON, nullable=True)  # List of server names
    server_ip = Column(String, nullable=True)  # Server IP for subscription links
    last_rotated = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

