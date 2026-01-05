from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./data/rootitvpn.db"
    
    # Security
    secret_key: str = "your-secret-key-change-this"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Admin
    admin_username: str = "admin"
    admin_password: str = "admin123"
    
    # Xray
    xray_grpc_address: str = "xray:8080"
    xray_config_path: str = "/etc/xray/config.json"
    xray_port: int = 443
    
    # Reality Settings
    reality_dest: str = "www.microsoft.com:443"
    reality_server_names: List[str] = [
        "www.microsoft.com",
        "www.cloudflare.com",
        "www.github.com"
    ]
    reality_rotation_hours: int = 24
    
    # Logging
    log_retention_hours: int = 24
    log_path: str = "/var/log/xray"
    
    # API
    api_v1_prefix: str = "/api/v1"
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
    ]
    
    # Subscription
    subscription_base_url: str = "http://localhost:8000"
    server_ip: str = ""  # Server IP for subscription links (should be set in .env)
    
    # Debug
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

