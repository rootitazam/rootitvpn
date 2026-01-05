from sqlalchemy.orm import Session
from app.models import XrayConfig
from app.utils.crypto import generate_reality_keys, generate_short_id
from app.config import settings
from datetime import datetime, timedelta
import secrets
import logging

logger = logging.getLogger(__name__)


class RealityService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_config(self) -> XrayConfig:
        """Get existing config or create new one"""
        config = self.db.query(XrayConfig).first()
        if not config:
            config = XrayConfig()
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)
        return config
    
    def generate_reality_settings(self) -> dict:
        """Generate new Reality settings"""
        private_key, public_key = generate_reality_keys()
        
        # Generate 2-4 short IDs
        num_short_ids = secrets.randbelow(3) + 2  # 2-4 short IDs
        short_ids = [generate_short_id() for _ in range(num_short_ids)]
        
        # Use configured server names or default
        server_names = settings.reality_server_names
        
        return {
            "private_key": private_key,
            "public_key": public_key,
            "short_ids": short_ids,
            "server_names": server_names,
            "dest": settings.reality_dest
        }
    
    def rotate_reality_settings(self) -> XrayConfig:
        """Rotate Reality settings (auto-rotation)"""
        config = self.get_or_create_config()
        
        # Check if rotation is needed
        if config.last_rotated:
            hours_since_rotation = (datetime.utcnow() - config.last_rotated).total_seconds() / 3600
            if hours_since_rotation < settings.reality_rotation_hours:
                logger.info(f"Rotation not needed yet. Last rotated {hours_since_rotation:.1f} hours ago")
                return config
        
        # Generate new settings
        new_settings = self.generate_reality_settings()
        
        # Update config
        config.reality_private_key = new_settings["private_key"]
        config.reality_public_key = new_settings["public_key"]
        config.reality_short_ids = new_settings["short_ids"]
        config.reality_server_names = new_settings["server_names"]
        config.reality_dest = new_settings["dest"]
        config.last_rotated = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(config)
        
        logger.info("Reality settings rotated successfully")
        return config
    
    def get_current_settings(self) -> dict:
        """Get current Reality settings"""
        config = self.get_or_create_config()
        
        # If no settings exist, generate them
        if not config.reality_public_key:
            config = self.rotate_reality_settings()
        
        return {
            "dest": config.reality_dest or settings.reality_dest,
            "private_key": config.reality_private_key,
            "public_key": config.reality_public_key,
            "short_ids": config.reality_short_ids or [],
            "server_names": config.reality_server_names or settings.reality_server_names
        }
    
    def update_dest(self, dest: str) -> XrayConfig:
        """Update Reality destination"""
        config = self.get_or_create_config()
        config.reality_dest = dest
        self.db.commit()
        self.db.refresh(config)
        return config
    
    def update_server_names(self, server_names: list) -> XrayConfig:
        """Update Reality server names"""
        config = self.get_or_create_config()
        config.reality_server_names = server_names
        self.db.commit()
        self.db.refresh(config)
        return config
    
    def update_server_ip(self, server_ip: str) -> XrayConfig:
        """Update server IP for subscription links"""
        config = self.get_or_create_config()
        config.server_ip = server_ip
        self.db.commit()
        self.db.refresh(config)
        logger.info(f"Server IP updated to: {server_ip}")
        return config
    
    def get_server_ip(self) -> str:
        """Get server IP from config or settings"""
        config = self.get_or_create_config()
        if config.server_ip:
            return config.server_ip
        # Fallback to settings if not in database
        return settings.server_ip or ""

