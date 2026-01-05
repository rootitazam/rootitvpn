"""
Stats Service for managing Xray statistics
Reads stats from Xray via gRPC and updates database
"""
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from app.models import User
from app.services.xray_grpc_client import XrayGRPCClient, XrayStatsParser
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class StatsService:
    """Service for managing and syncing Xray statistics"""
    
    def __init__(self, db: Session):
        self.db = db
        self.grpc_client = None
    
    def _get_grpc_client(self) -> Optional[XrayGRPCClient]:
        """Get or create gRPC client"""
        if not self.grpc_client:
            try:
                self.grpc_client = XrayGRPCClient()
            except Exception as e:
                logger.error(f"Failed to create gRPC client: {e}")
                return None
        return self.grpc_client
    
    def sync_user_stats(self, user: User) -> bool:
        """Sync stats for a single user from Xray to database"""
        try:
            client = self._get_grpc_client()
            if not client:
                logger.warning("gRPC client not available, skipping stats sync")
                return False
            
            # Get stats from Xray
            stats = client.get_user_stats(user.uuid)
            
            if stats:
                # Update user data_used
                user.data_used = stats.get('total', 0)
                self.db.commit()
                logger.debug(f"Synced stats for user {user.username}: {stats['total']} bytes")
                return True
            else:
                logger.warning(f"No stats found for user {user.uuid}")
                return False
        except Exception as e:
            logger.error(f"Error syncing stats for user {user.id}: {e}")
            self.db.rollback()
            return False
    
    def sync_all_users_stats(self) -> int:
        """Sync stats for all active users"""
        try:
            client = self._get_grpc_client()
            if not client:
                logger.warning("gRPC client not available, skipping stats sync")
                return 0
            
            # Get all users stats from Xray
            all_stats = client.get_all_users_stats()
            
            if not all_stats:
                logger.warning("No stats received from Xray")
                return 0
            
            # Update database for each user
            updated_count = 0
            for user_uuid, stats in all_stats.items():
                user = self.db.query(User).filter(User.uuid == user_uuid).first()
                if user:
                    user.data_used = stats.get('total', 0)
                    updated_count += 1
            
            self.db.commit()
            logger.info(f"Synced stats for {updated_count} users")
            return updated_count
        except Exception as e:
            logger.error(f"Error syncing all users stats: {e}")
            self.db.rollback()
            return 0
    
    def get_user_traffic(self, user_uuid: str) -> Dict[str, int]:
        """Get current traffic stats for a user"""
        try:
            client = self._get_grpc_client()
            if not client:
                return {'uplink': 0, 'downlink': 0, 'total': 0}
            
            return client.get_user_stats(user_uuid)
        except Exception as e:
            logger.error(f"Error getting user traffic: {e}")
            return {'uplink': 0, 'downlink': 0, 'total': 0}
    
    def get_online_users(self) -> List[str]:
        """Get list of online user UUIDs"""
        try:
            client = self._get_grpc_client()
            if not client:
                return []
            
            # Get all users stats - users with recent activity are considered online
            all_stats = client.get_all_users_stats()
            # Filter users with recent traffic (in last 5 minutes)
            # This is a simplified check - in production, you'd check last activity time
            online_users = [uuid for uuid, stats in all_stats.items() if stats.get('total', 0) > 0]
            return online_users
        except Exception as e:
            logger.error(f"Error getting online users: {e}")
            return []
    
    def reset_user_stats(self, user_uuid: str) -> bool:
        """Reset stats for a user in Xray"""
        try:
            client = self._get_grpc_client()
            if not client:
                return False
            
            # Reset stats by getting with reset=True
            client.get_stats(f"user>>>{user_uuid}>>>traffic>>>uplink", reset=True)
            client.get_stats(f"user>>>{user_uuid}>>>traffic>>>downlink", reset=True)
            
            # Also update database
            user = self.db.query(User).filter(User.uuid == user_uuid).first()
            if user:
                user.data_used = 0
                self.db.commit()
            
            logger.info(f"Reset stats for user {user_uuid}")
            return True
        except Exception as e:
            logger.error(f"Error resetting user stats: {e}")
            return False
    
    def close(self):
        """Close gRPC connection"""
        if self.grpc_client:
            self.grpc_client.close()
            self.grpc_client = None

