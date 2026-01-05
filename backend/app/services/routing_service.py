from typing import List, Dict
import json
import logging

logger = logging.getLogger(__name__)


class RoutingService:
    """Service for managing routing rules, especially for Iran IPs and domains"""
    
    @staticmethod
    def get_iran_routing_rules() -> List[Dict]:
        """Get routing rules for Iran IPs and .ir domains (DIRECT)"""
        return [
            {
                "type": "field",
                "ip": ["geoip:ir"],
                "outboundTag": "direct"
            },
            {
                "type": "field",
                "domain": ["geosite:ir"],
                "outboundTag": "direct"
            }
        ]
    
    @staticmethod
    def get_blocked_rules() -> List[Dict]:
        """Get rules for blocking ads"""
        return [
            {
                "type": "field",
                "domain": ["geosite:category-ads-all"],
                "outboundTag": "blocked"
            }
        ]
    
    @staticmethod
    def build_routing_config(include_iran_direct: bool = True, include_ads_block: bool = True) -> Dict:
        """Build complete routing configuration"""
        rules = []
        
        if include_iran_direct:
            rules.extend(RoutingService.get_iran_routing_rules())
        
        if include_ads_block:
            rules.extend(RoutingService.get_blocked_rules())
        
        return {
            "domainStrategy": "IPIfNonMatch",
            "rules": rules
        }
    
    @staticmethod
    def add_custom_rule(rules: List[Dict], rule: Dict) -> List[Dict]:
        """Add a custom routing rule"""
        rules.append(rule)
        return rules
    
    @staticmethod
    def remove_rule_by_tag(rules: List[Dict], tag: str) -> List[Dict]:
        """Remove routing rule by outbound tag"""
        return [rule for rule in rules if rule.get("outboundTag") != tag]

