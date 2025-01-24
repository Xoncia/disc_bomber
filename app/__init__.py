from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config
from app.database.session import db
from app.routes.dynamic_routes import register_dynamic_routes

def create_app(config_class: type[Config] = Config) -> Flask:
    """
    Factory function that creates and configures the Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)

    # Register blueprints
    register_dynamic_routes(app)

    return app 