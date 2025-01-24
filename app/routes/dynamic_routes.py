from datetime import datetime
import time
from typing import Any, Dict, List
from flask import Flask, render_template, Blueprint
from app.services.route_service import RouteService
from app.services.discord_service import DiscordService
from app.modules import ModuleRegistry, discover_modules

main = Blueprint('main', __name__)
route_service = RouteService()
discord_service = DiscordService()

def get_modules_data() -> Dict[str, Any]:
    """Get data about all registered modules"""
    modules = ModuleRegistry.get_all_modules()
    return {
        'integrated': [m for m in modules if m.is_integrated],
        'custom': [m for m in modules if not m.is_integrated],
        'total_count': len(modules),
        'active_count': len([m for m in modules if m.is_active])
    }

@main.route('/')
def index() -> str:
    return render_template('pages/dashboard.html', **get_dashboard_data())

def get_dashboard_data() -> dict:
    """Get data for dashboard display"""
    status = route_service.get_system_status()
    modules = get_modules_data()

    total_routes = sum(len(module.endpoints) for module in ModuleRegistry.get_all_modules())
    
    return {
        'stats': {
            'total_routes': total_routes,
            'uptime': status['uptime'],
            'status': status['status'],
            'is_healthy': status['is_healthy']
        },
        'modules': modules
    }

@main.route('/routes-manager')
def routes_manager() -> str:
    modules = get_modules_data()
    return render_template('pages/routes_manager.html', modules=modules)

@main.route('/api-testing')
def api_testing() -> str:
    modules = get_modules_data()
    return render_template('pages/api_testing.html', modules=modules)

@main.route('/settings')
def settings() -> str:
    return render_template('pages/settings.html')

@main.route('/discord-manager')
def discord_manager() -> str:
    """Discord tools management page"""
    tokens = discord_service.get_tokens()
    return render_template('pages/discord_manager.html', tokens=tokens)

def register_dynamic_routes(app: Flask) -> None:
    """Register dynamic routes and modules in the application"""
    discover_modules()  # Discover and load all modules
    
    # Register module blueprints
    for module in ModuleRegistry.get_all_modules():
        if module.blueprint:
            app.register_blueprint(module.blueprint)
    
    # Register main blueprint
    app.register_blueprint(main)
    
    # Update endpoints after all blueprints are registered
    ModuleRegistry.update_endpoints(app) 