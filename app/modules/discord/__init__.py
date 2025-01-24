from flask import Blueprint, jsonify, request
from app.schemas import MessageResponse, ErrorDetail
from app.services.discord_service import DiscordService

# Create blueprint for Discord routes
discord_routes = Blueprint('discord', __name__, url_prefix='/api/discord')
discord_service = DiscordService()

@discord_routes.route('/webhook', methods=['POST'])
def webhook():
    """Handle Discord webhook"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(MessageResponse.error_response(
                message="No webhook data provided",
                code="INVALID_WEBHOOK"
            ).model_dump())
        return jsonify(MessageResponse.success_response(
            data={"status": "received"},
            message="Webhook processed successfully"
        ).model_dump())
    except Exception as e:
        return jsonify(MessageResponse.error_response(
            message="Failed to process webhook",
            errors=[ErrorDetail(message=str(e), code="WEBHOOK_ERROR")]
        ).model_dump())

@discord_routes.route('/tokens', methods=['GET'])
def list_tokens():
    """List all Discord tokens"""
    try:
        tokens = discord_service.get_tokens()
        return jsonify(MessageResponse.success_response(
            data={
                "tokens": [token.model_dump() for token in tokens],
                "total": len(tokens)
            },
            message="Tokens retrieved successfully"
        ).model_dump())
    except Exception as e:
        return jsonify(MessageResponse.error_response(
            message="Failed to retrieve tokens",
            errors=[ErrorDetail(message=str(e), code="TOKEN_LIST_ERROR")]
        ).model_dump())

@discord_routes.route('/tokens', methods=['POST'])
def create_token():
    """Create a new Discord token"""
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'token' not in data:
            return jsonify(MessageResponse.error_response(
                message="Name and token are required",
                code="INVALID_REQUEST"
            ).model_dump()), 400
        
        token = discord_service.create_token(data['name'], data['token'])
        return jsonify(MessageResponse.success_response(
            data={
                "token": {
                    "id": token.id,
                    "name": token.name,
                    "created_at": token.created_at
                }
            },
            message="Token created successfully"
        ).model_dump()), 201
    except Exception as e:
        return jsonify(MessageResponse.error_response(
            message="Failed to create token",
            errors=[ErrorDetail(message=str(e), code="TOKEN_CREATION_ERROR")]
        ).model_dump()), 500

@discord_routes.route('/tokens/<token_id>', methods=['DELETE'])
def delete_token(token_id: str):
    """Delete a Discord token"""
    try:
        if discord_service.delete_token(token_id):
            return jsonify(MessageResponse.success_response(
                message="Token deleted successfully"
            ).model_dump())
        return jsonify(MessageResponse.error_response(
            message="Token not found",
            code="TOKEN_NOT_FOUND"
        ).model_dump()), 404
    except Exception as e:
        return jsonify(MessageResponse.error_response(
            message="Failed to delete token",
            errors=[ErrorDetail(message=str(e), code="TOKEN_DELETION_ERROR")]
        ).model_dump()), 500

@discord_routes.route('/messages/delete', methods=['POST'])
def delete_messages():
    """Delete Discord messages"""
    try:
        data = request.get_json()
        if not data or 'channelType' not in data or 'channelId' not in data or 'count' not in data:
            return jsonify(MessageResponse.error_response(
                message="Channel type, channel ID and count are required",
                code="INVALID_REQUEST"
            ).model_dump()), 400

        discord_service.delete_messages(
            data['channelType'],
            data['channelId'],
            data['count']
        )
        return jsonify(MessageResponse.success_response(
            message="Messages deleted successfully"
        ).model_dump())
    except Exception as e:
        return jsonify(MessageResponse.error_response(
            message="Failed to delete messages",
            errors=[ErrorDetail(message=str(e), code="MESSAGE_DELETE_ERROR")]
        ).model_dump())

@discord_routes.route('/messages/scrape', methods=['POST'])
def scrape_messages():
    """Scrape Discord messages"""
    try:
        data = request.get_json()
        if not data or 'type' not in data or 'targetId' not in data or 'format' not in data:
            return jsonify(MessageResponse.error_response(
                message="Target type, target ID and format are required",
                code="INVALID_REQUEST"
            ).model_dump()), 400

        messages = discord_service.scrape_messages(
            data['type'],
            data['targetId'],
            data['format']
        )
        return jsonify(messages)
    except Exception as e:
        return jsonify(MessageResponse.error_response(
            message="Failed to scrape messages",
            errors=[ErrorDetail(message=str(e), code="MESSAGE_SCRAPE_ERROR")]
        ).model_dump())

def setup_module():
    """Register this module with the system"""
    from app.modules import ModuleRegistry, ModuleInfo
    
    ModuleRegistry.register(ModuleInfo(
        name="Discord Integration",
        description="Discord bot and webhook integration endpoints",
        version="1.0.0",
        author="System",
        icon="fab fa-discord",
        routes_count=6,  # Updated route count
        is_integrated=True,
        blueprint=discord_routes
    )) 