import base64
import json
import qrcode
from io import BytesIO
from typing import Dict
from app.models import User
from app.services.reality_service import RealityService
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class SubscriptionService:
    def __init__(self, reality_service: RealityService):
        self.reality_service = reality_service
    
    def generate_vless_config(self, user: User, server_ip: str = None) -> Dict:
        """Generate VLESS config for a user"""
        # Use server_ip from parameter, or from database config, or from settings, or default
        if not server_ip:
            # First try to get from database
            server_ip = self.reality_service.get_server_ip()
            # If not in database, try settings
            if not server_ip:
                server_ip = settings.server_ip or "your-server-ip"
            if server_ip == "your-server-ip":
                logger.warning("SERVER_IP not set in config, using placeholder")
        
        reality_settings = self.reality_service.get_current_settings()
        
        # Select a random short ID
        import secrets
        short_id = secrets.choice(reality_settings["short_ids"]) if reality_settings["short_ids"] else ""
        
        config = {
            "v": "2",
            "ps": f"RootitVPN-{user.username}",
            "add": server_ip,
            "port": str(settings.xray_port),
            "id": user.uuid,
            "aid": "0",
            "scy": "none",
            "net": "tcp",
            "type": "none",
            "host": reality_settings["dest"].split(":")[0],
            "path": "",
            "tls": "reality",
            "sni": secrets.choice(reality_settings["server_names"]) if reality_settings["server_names"] else "",
            "alpn": "",
            "fp": "chrome",
            "pbk": reality_settings["public_key"],
            "sid": short_id,
            "spx": ""
        }
        
        return config
    
    def generate_v2rayng_link(self, user: User, server_ip: str = None) -> str:
        """Generate v2rayNG subscription link"""
        config = self.generate_vless_config(user, server_ip)
        
        # v2rayNG format: vless://uuid@server:port?params
        params = [
            f"type={config['net']}",
            f"security={config['tls']}",
            f"sni={config['sni']}",
            f"fp={config['fp']}",
            f"pbk={config['pbk']}",
            f"sid={config['sid']}",
            f"spx={config['spx']}"
        ]
        
        link = f"vless://{config['id']}@{config['add']}:{config['port']}?{'&'.join(params)}#{config['ps']}"
        return link
    
    def generate_shadowrocket_link(self, user: User, server_ip: str = None) -> str:
        """Generate Shadowrocket subscription link"""
        config = self.generate_vless_config(user, server_ip)
        reality_settings = self.reality_service.get_current_settings()
        
        # Shadowrocket format
        params = [
            f"encryption=none",
            f"type=tcp",
            f"security=reality",
            f"sni={config['sni']}",
            f"fp={config['fp']}",
            f"pbk={config['pbk']}",
            f"sid={config['sid']}"
        ]
        
        link = f"vless://{config['id']}@{config['add']}:{config['port']}?{'&'.join(params)}#{config['ps']}"
        return link
    
    def generate_nekoray_link(self, user: User, server_ip: str = None) -> str:
        """Generate Nekoray subscription link (same as v2rayNG)"""
        return self.generate_v2rayng_link(user, server_ip)
    
    def generate_subscription_links(self, user: User, server_ip: str = None) -> Dict[str, str]:
        """Generate all subscription links for a user"""
        return {
            "v2rayng": self.generate_v2rayng_link(user, server_ip),
            "shadowrocket": self.generate_shadowrocket_link(user, server_ip),
            "nekoray": self.generate_nekoray_link(user, server_ip)
        }
    
    def generate_qr_code(self, link: str) -> str:
        """Generate QR code as base64 string"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(link)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def generate_subscription_response(self, user: User, server_ip: str = None) -> Dict:
        """Generate complete subscription response with all formats and QR code"""
        links = self.generate_subscription_links(user, server_ip)
        
        # Generate QR code for v2rayNG link (most common)
        qr_code = self.generate_qr_code(links["v2rayng"])
        
        return {
            "v2rayng": links["v2rayng"],
            "shadowrocket": links["shadowrocket"],
            "nekoray": links["nekoray"],
            "qr_code": qr_code
        }

