from flask import Flask
from config import Config
from app.database import init_db


def create_app(config_class=Config) -> Flask:
    """
    Application Factory Pattern function for initializing the Flask web app.
    
    :param config_class: Configuration class reference
    :return: Flask app instance
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize database schema
    with app.app_context():
        init_db()

    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
