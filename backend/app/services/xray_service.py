import json
import grpc
import os
from typing import List, Dict, Optional
from pathlib import Path
from app.models import User, XrayConfig
from app.services.reality_service import RealityService
from app.services.routing_service import RoutingService
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Note: Xray gRPC proto files need to be compiled
# For now, we'll use JSON-based config management
# gRPC integration can be added later with proper proto compilation


class XrayService:
    def __init__(self, reality_service: RealityService, routing_service: RoutingService):
        self.reality_service = reality_service
        self.routing_service = routing_service
        self.config_path = Path(settings.xray_config_path)
    
    def load_config_template(self) -> Dict:
        """Load Xray config template"""
        template_path = Path(__file__).parent.parent.parent.parent / "xray" / "config.json.template"
        
        if not template_path.exists():
            logger.warning("Template not found, using default config")
            return self.get_default_config()
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_default_config(self) -> Dict:
        """Get default Xray config"""
        return {
            "log": {
                "loglevel": "warning",
                "access": "/var/log/xray/access.log",
                "error": "/var/log/xray/error.log"
            },
            "stats": {},
            "api": {
                "tag": "api",
                "services": ["StatsService", "HandlerService"]
            },
            "inbounds": [{
                "tag": "vless-reality",
                "port": 443,
                "protocol": "vless",
                "settings": {
                    "clients": [],
                    "decryption": "none"
                },
                "streamSettings": {
                    "network": "tcp",
                    "security": "reality",
                    "realitySettings": {},
                    "sockopt": {
                        "tcpFastOpen": True
                    }
                },
                "fragment": {
                    "packets": "tlshello",
                    "length": "100-200",
                    "interval": "10-20"
                }
            }],
            "outbounds": [
                {"protocol": "freedom", "tag": "direct"},
                {"protocol": "blackhole", "tag": "blocked"}
            ],
            "routing": {
                "domainStrategy": "IPIfNonMatch",
                "rules": []
            }
        }
    
    def build_user_client_config(self, user: User) -> Dict:
        """Build Xray client config for a user"""
        return {
            "id": user.uuid,
            "email": user.username,
            "flow": "xtls-rprx-vision"
        }
    
    def generate_config(self, users: List[User]) -> Dict:
        """Generate complete Xray config with all users"""
        config = self.load_config_template()
        reality_settings = self.reality_service.get_current_settings()
        
        # Build clients list
        clients = [self.build_user_client_config(user) for user in users if user.is_active]
        
        # Update inbound settings
        if config.get("inbounds"):
            for inbound in config["inbounds"]:
                if inbound.get("protocol") == "vless":
                    inbound["settings"]["clients"] = clients
                    
                    # Update Reality settings
                    if "realitySettings" in inbound.get("streamSettings", {}):
                        inbound["streamSettings"]["realitySettings"] = {
                            "dest": reality_settings["dest"],
                            "serverNames": reality_settings["server_names"],
                            "privateKey": reality_settings["private_key"],
                            "shortIds": reality_settings["short_ids"],
                            "show": False
                        }
        
        # Update routing rules
        config["routing"] = self.routing_service.build_routing_config()
        
        return config
    
    def save_config(self, config: Dict) -> bool:
        """Save Xray config to file"""
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write config
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Xray config saved to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving Xray config: {e}")
            return False
    
    def ensure_config_exists(self, db: Session) -> bool:
        """Ensure Xray config file exists, create if not"""
        if self.config_path.exists():
            return True
        
        try:
            # Generate config with current users
            from app.models import User
            users = db.query(User).filter(User.is_active == True).all()
            config = self.generate_config(users)
            return self.save_config(config)
        except Exception as e:
            logger.error(f"Error ensuring config exists: {e}")
            return False
    
    def reload_config(self) -> bool:
        """Reload Xray config using gRPC or docker restart"""
        try:
            # Try using gRPC first
            from app.services.xray_grpc_client import XrayGRPCClient
            client = XrayGRPCClient()
            if client.reload_config():
                logger.info("Xray config reloaded via gRPC")
                client.close()
                return True
            client.close()
        except Exception as e:
            logger.warning(f"gRPC reload failed: {e}, trying docker restart")
        
        # Fallback: Restart Xray container via docker
        try:
            import subprocess
            result = subprocess.run(
                ["docker", "restart", "rootitvpn-xray"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                logger.info("Xray container restarted successfully")
                return True
            else:
                logger.error(f"Failed to restart Xray container: {result.stderr}")
                return False
        except FileNotFoundError:
            logger.warning("Docker command not found, cannot restart container")
            return False
        except subprocess.TimeoutExpired:
            logger.error("Timeout while restarting Xray container")
            return False
        except Exception as e:
            logger.error(f"Error restarting Xray container: {e}")
            return False
    
    def get_user_stats(self, user: User) -> Dict:
        """Get user statistics from Xray (via gRPC or logs)"""
        # This would query Xray's StatsService via gRPC
        # For now, return basic info
        return {
            "uuid": user.uuid,
            "data_used": user.data_used,
            "data_limit": user.data_limit,
            "is_active": user.is_active
        }
    
    def update_user_data_usage(self, user_uuid: str, bytes_sent: int, bytes_received: int):
        """Update user data usage (called from stats or logs)"""
        # This would be called periodically from Xray stats
        total_bytes = bytes_sent + bytes_received
        # Update logic would be in the user service/router
        logger.debug(f"User {user_uuid} used {total_bytes} bytes")

