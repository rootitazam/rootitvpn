"""
Xray gRPC Client for StatsService and HandlerService
Note: This is a simplified implementation. For full functionality,
Xray proto files need to be compiled and imported.
"""
import grpc
from typing import Dict, Optional, List
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class XrayGRPCClient:
    """gRPC client for Xray StatsService and HandlerService"""
    
    def __init__(self, address: str = None):
        self.address = address or settings.xray_grpc_address
        self.channel = None
        self._connect()
    
    def _connect(self):
        """Establish gRPC connection"""
        try:
            # Parse address (format: host:port)
            if ':' not in self.address:
                self.address = f"{self.address}:8080"
            
            host, port = self.address.split(':')
            self.channel = grpc.insecure_channel(f"{host}:{port}")
            logger.info(f"Connected to Xray gRPC at {self.address}")
        except Exception as e:
            logger.error(f"Failed to connect to Xray gRPC: {e}")
            self.channel = None
    
    def get_stats(self, pattern: str = "", reset: bool = False) -> Dict[str, int]:
        """
        Get stats from Xray StatsService
        Pattern format: "user>>>{uuid}>>>traffic>>>uplink" or "user>>>{uuid}>>>traffic>>>downlink"
        Returns dict of stat_name: value
        """
        if not self.channel:
            logger.warning("gRPC channel not connected")
            return {}
        
        try:
            # Note: This requires Xray proto files to be compiled
            # For now, we'll use a workaround with HTTP API or log parsing
            # In production, you should compile Xray proto files:
            # from app.proto import stats_pb2, stats_pb2_grpc
            # stub = stats_pb2_grpc.StatsServiceStub(self.channel)
            # response = stub.GetStats(stats_pb2.GetStatsRequest(name=pattern, reset=reset))
            
            logger.debug(f"Getting stats with pattern: {pattern}, reset: {reset}")
            # Placeholder - will be implemented with proper proto files
            return {}
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def get_user_stats(self, user_uuid: str) -> Dict[str, int]:
        """Get traffic stats for a specific user"""
        stats = {}
        
        # Get uplink (bytes sent)
        uplink_pattern = f"user>>>{user_uuid}>>>traffic>>>uplink"
        uplink_stats = self.get_stats(uplink_pattern)
        stats['uplink'] = uplink_stats.get(uplink_pattern, 0)
        
        # Get downlink (bytes received)
        downlink_pattern = f"user>>>{user_uuid}>>>traffic>>>downlink"
        downlink_stats = self.get_stats(downlink_pattern)
        stats['downlink'] = downlink_stats.get(downlink_pattern, 0)
        
        stats['total'] = stats['uplink'] + stats['downlink']
        return stats
    
    def get_all_users_stats(self) -> Dict[str, Dict[str, int]]:
        """Get stats for all users"""
        # Get all user stats
        all_stats_pattern = "user>>>"
        all_stats = self.get_stats(all_stats_pattern)
        
        # Parse and organize by user UUID
        users_stats = {}
        for stat_name, value in all_stats.items():
            if "user>>>" in stat_name and "traffic" in stat_name:
                parts = stat_name.split(">>>")
                if len(parts) >= 2:
                    user_uuid = parts[1]
                    if user_uuid not in users_stats:
                        users_stats[user_uuid] = {'uplink': 0, 'downlink': 0, 'total': 0}
                    
                    if 'uplink' in stat_name:
                        users_stats[user_uuid]['uplink'] = value
                    elif 'downlink' in stat_name:
                        users_stats[user_uuid]['downlink'] = value
                    
                    users_stats[user_uuid]['total'] = (
                        users_stats[user_uuid]['uplink'] + 
                        users_stats[user_uuid]['downlink']
                    )
        
        return users_stats
    
    def reload_config(self) -> bool:
        """Reload Xray configuration via HandlerService"""
        if not self.channel:
            logger.warning("gRPC channel not connected")
            return False
        
        try:
            # Note: This requires Xray proto files
            # from app.proto import handler_pb2, handler_pb2_grpc
            # stub = handler_pb2_grpc.HandlerServiceStub(self.channel)
            # response = stub.AlterInbound(handler_pb2.AlterInboundRequest(...))
            
            logger.info("Reloading Xray config via gRPC")
            # Placeholder - will be implemented with proper proto files
            return True
        except Exception as e:
            logger.error(f"Error reloading config: {e}")
            return False
    
    def close(self):
        """Close gRPC connection"""
        if self.channel:
            self.channel.close()
            logger.info("Closed Xray gRPC connection")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Alternative implementation using log parsing for stats
# This can be used until proto files are compiled
class XrayStatsParser:
    """Parse Xray stats from logs or alternative methods"""
    
    @staticmethod
    def parse_access_log(log_path: str) -> Dict[str, Dict[str, int]]:
        """Parse access log to extract user traffic stats"""
        # This would parse Xray access logs
        # Format: timestamp user_uuid domain bytes_sent bytes_received
        users_stats = {}
        
        try:
            with open(log_path, 'r') as f:
                for line in f:
                    # Parse log line (format depends on Xray log format)
                    # This is a placeholder implementation
                    pass
        except Exception as e:
            logger.error(f"Error parsing access log: {e}")
        
        return users_stats

