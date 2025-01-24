from flask import Blueprint, jsonify
from app.modules import ModuleInfo, ModuleRegistry

# Create a blueprint for this module
bp = Blueprint('example', __name__, url_prefix='/api/example')

# Define routes for this module
@bp.route('/hello', methods=['GET'])
def hello():
    return jsonify({
        "message": "Hello from example module!"
    })

@bp.route('/echo', methods=['POST'])
def echo():
    return jsonify({
        "message": "Echo from example module!"
    })

def setup_module():
    """Register this module with the system"""
    ModuleRegistry.register(ModuleInfo(
        name="Example Module",
        description="An example module showing how to create custom endpoints",
        version="1.0.0",
        author="User",
        icon="fas fa-flask",
        routes_count=2,
        blueprint=bp
    )) 