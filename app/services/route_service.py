from typing import Any, Dict, List
from flask import jsonify, Blueprint, current_app
from datetime import datetime, timedelta
import time
import inspect

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

    def _parse_docstring(self, docstring: str) -> Dict[str, Any]:
        """Parse a docstring to extract description and parameters."""
        if not docstring:
            return {"description": "No description available.", "params": []}

        lines = [line.strip() for line in docstring.split("\n")]
        
        description = []
        params = []
        current_section = "description"
        
        for line in lines:
            if not line and not description:
                continue
                
            if line.startswith("Parameters:"):
                current_section = "params"
                continue
            elif line.startswith("Returns:"):
                current_section = "returns"
                continue
            
            if current_section == "description":
                if line:
                    description.append(line)
            elif current_section == "params" and ":" in line and not line.endswith(":"):
                param_name, param_desc = line.split(":", 1)
                param_type = "string"
                if "(" in param_name and ")" in param_name:
                    param_name, param_type = param_name.split("(")
                    param_type = param_type.rstrip(")")
                params.append({
                    "name": param_name.strip(),
                    "type": param_type.strip(),
                    "description": param_desc.strip()
                })

        full_description = " ".join(description).strip()
        
        return {
            "description": full_description if full_description else "No description available.",
            "params": params
        }

    def get_registered_routes(self) -> List[dict]:
        """Returns a list of all registered routes with their metadata"""
        app = current_app._get_current_object()
        routes = []
        
        for rule in app.url_map.iter_rules():
            if rule.rule.startswith('/api/'):
                view_func = app.view_functions[rule.endpoint]
                
                docstring_info = self._parse_docstring(view_func.__doc__)
                
                module_name = "Basic Routes"
                module_icon = "fas fa-link"
                if "." in rule.endpoint:
                    module_name = rule.endpoint.split(".")[0].replace("_", " ").title()
                    if "discord" in module_name.lower():
                        module_icon = "fab fa-discord"
                
                routes.append({
                    'path': str(rule),
                    'endpoint': rule.endpoint,
                    'methods': sorted(list(rule.methods - {'HEAD', 'OPTIONS'})),
                    'description': docstring_info['description'],
                    'params': docstring_info['params'],
                    'module': {
                        'name': module_name,
                        'icon': module_icon
                    }
                })
        
        return sorted(routes, key=lambda x: x['endpoint']) 