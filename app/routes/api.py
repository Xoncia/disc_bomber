from typing import Any
from flask import Blueprint, jsonify, request
from app.services.route_service import RouteService
from datetime import datetime
from app.schemas import HealthResponse, HealthStatus, MessageResponse, BaseResponse, ErrorDetail
from app.services.discord_service import DiscordService
from app.schemas.discord import TokenSchema

api = Blueprint('api', __name__, url_prefix='/api')
route_service = RouteService()
discord_service = DiscordService()

@api.route('/routes', methods=['GET'])
def list_routes() -> dict:
    """List all registered API routes"""
    try:
        routes = route_service.get_registered_routes()
        return jsonify(MessageResponse.success_response(
            data={
                "total": len(routes),
                "routes": routes
            },
            message="Routes retrieved successfully"
        ).model_dump())
    except Exception as e:
        return jsonify(MessageResponse.error_response(
            message="Failed to retrieve routes",
            errors=[ErrorDetail(message=str(e), code="ROUTE_LIST_ERROR")]
        ).model_dump())

@api.route('/stats', methods=['GET'])
def get_stats() -> dict:
    """Get system statistics and health status"""
    try:
        status = route_service.get_system_status()
        uptime = route_service.get_uptime()
        routes = route_service.get_registered_routes()
        
        health_status = HealthStatus(
            status=status['status'],
            uptime=uptime['formatted'],
            uptime_seconds=uptime['seconds'],
            is_healthy=status['is_healthy'],
            last_check=status['last_health_check']
        )
        
        return jsonify(HealthResponse.success_response(
            data=health_status,
            message="System status retrieved successfully"
        ).model_dump())
    except Exception as e:
        return jsonify(HealthResponse.error_response(
            message="Failed to retrieve system status",
            errors=[ErrorDetail(message=str(e), code="STATS_ERROR")]
        ).model_dump())
