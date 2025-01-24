from typing import Dict, List, Optional, Type
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
                            module_info.endpoints.append(EndpointInfo(
                                url=str(rule.rule),
                                method=method,
                                name=rule.endpoint
                            ))
                
                # Update routes count
                module_info.routes_count = len(module_info.endpoints)

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