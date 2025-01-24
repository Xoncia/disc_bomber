from typing import Any, Dict, List
from flask import jsonify, Blueprint, current_app
from datetime import datetime, timedelta
import time

class RouteService:
    """Service for managing route modules"""

    _start_time = time.time()
    _last_health_check = time.time()
    _is_healthy = True

    @classmethod
    def get_uptime(cls) -> Dict[str, Any]:
        """Get formatted uptime and raw seconds"""
        uptime_seconds = int(time.time() - cls._start_time)
        
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, _ = divmod(remainder, 60)

        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0 or days > 0:
            parts.append(f"{hours}h")
        parts.append(f"{minutes}m")
        
        formatted_uptime = " ".join(parts)
        
        return {
            "formatted": formatted_uptime,
            "seconds": uptime_seconds
        }

    @classmethod
    def get_system_status(cls) -> Dict[str, Any]:
        """Get system status including uptime and health"""
        uptime = cls.get_uptime()
        current_time = time.time()
        
        # Update health check timestamp
        cls._last_health_check = current_time
        
        return {
            'uptime': uptime["formatted"],
            'uptime_seconds': uptime["seconds"],
            'status': 'Operational',
            'is_healthy': True,
            'last_health_check': datetime.fromtimestamp(current_time)
        }

    def get_registered_routes(self) -> List[dict]:
        """Returns a list of all registered routes"""
        app = current_app._get_current_object()
        routes = []
        
        for rule in app.url_map.iter_rules():
            if rule.rule.startswith('/api/'):
                routes.append({
                    'path': str(rule),
                    'endpoint': rule.endpoint,
                    'methods': sorted(list(rule.methods - {'HEAD', 'OPTIONS'}))
                })
        
        return sorted(routes, key=lambda x: x['endpoint']) 