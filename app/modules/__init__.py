from typing import Dict, List, Optional, Type, Any
from dataclasses import dataclass, field
from flask import Blueprint, current_app, jsonify, request
import importlib
import os
import pkgutil
from pathlib import Path
from datetime import datetime
from app.schemas import HealthResponse, HealthStatus, MessageResponse, BaseResponse, ErrorDetail

@dataclass
class EndpointInfo:
    url: str
    method: str
    name: str
    description: str = ""
    params: List[Dict[str, str]] = field(default_factory=list)

@dataclass
class ModuleInfo:
    name: str
    description: str
    version: str
    author: str
    icon: str
    routes_count: int
    is_integrated: bool = False
    is_active: bool = True
    blueprint: Optional[Blueprint] = None
    endpoints: List[EndpointInfo] = field(default_factory=list)

class ModuleRegistry:
    _modules: Dict[str, ModuleInfo] = {}
    
    @classmethod
    def register(cls, module_info: ModuleInfo) -> None:
        """Register a new module"""
        # Store the module info first
        cls._modules[module_info.name] = module_info
    
    @classmethod
    def get_all_modules(cls) -> List[ModuleInfo]:
        """Get all registered modules"""
        return list(cls._modules.values())
    
    @classmethod
    def get_module(cls, name: str) -> Optional[ModuleInfo]:
        """Get a specific module by name"""
        return cls._modules.get(name)
    
    @classmethod
    def update_endpoints(cls, app) -> None:
        """Update endpoints for all modules after they're registered with the app"""
        for module_info in cls._modules.values():
            if module_info.blueprint:
                module_info.endpoints.clear()
                
                # Look through app's url map for routes belonging to this blueprint
                for rule in app.url_map.iter_rules():
                    if rule.endpoint.startswith(module_info.blueprint.name + '.'):
                        for method in rule.methods - {'HEAD', 'OPTIONS'}:
                            view_func = app.view_functions[rule.endpoint]
                            docstring_info = cls._parse_docstring(view_func.__doc__)
                            
                            module_info.endpoints.append(EndpointInfo(
                                url=str(rule.rule),
                                method=method,
                                name=rule.endpoint,
                                description=docstring_info.get('description', ''),
                                params=docstring_info.get('params', [])
                            ))
                
                # Update routes count
                module_info.routes_count = len(module_info.endpoints)

    @staticmethod
    def _parse_docstring(docstring: str) -> Dict[str, Any]:
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

def discover_modules() -> None:
    """Discover and load all modules in the modules directory"""
    modules_dir = Path(__file__).parent
    
    # Load built-in modules first
    register_builtin_modules()
    
    # Then load external modules
    for module_finder, name, _ in pkgutil.iter_modules([str(modules_dir)]):
        if name != "__init__":
            try:
                module = importlib.import_module(f"app.modules.{name}")
                if hasattr(module, "setup_module"):
                    module.setup_module()
            except Exception as e:
                print(f"Failed to load module {name}: {e}")

def register_builtin_modules() -> None:
    """Register the built-in modules"""
    from app.routes.api import api
    
    ModuleRegistry.register(ModuleInfo(
        name="Basic Routes",
        description="Core API endpoints for system operations and statistics",
        version="1.0.0",
        author="System",
        icon="fas fa-cube",
        routes_count=2,
        is_integrated=True,
        blueprint=api
    )) 