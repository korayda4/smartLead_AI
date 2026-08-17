from flask import Flask, request
from config import Config
from app.database import init_db
from flask_cors import CORS


def create_app(config_class=Config) -> Flask:
    """
    Application Factory Pattern function for initializing the Flask web app.
    
    :param config_class: Configuration class reference
    :return: Flask app instance
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Comprehensive CORS configuration for all origins (Wix, custom domains, localhost)
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        supports_credentials=False,
        allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    # Universal CORS header injector ensuring every response has CORS headers
    @app.after_request
    def apply_cors_headers(response):
        origin = request.headers.get("Origin")
        response.headers["Access-Control-Allow-Origin"] = origin if origin else "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, Accept"
        return response

    # Global OPTIONS preflight handler
    @app.before_request
    def handle_options_preflight():
        if request.method == "OPTIONS":
            response = app.make_response(("", 204))
            origin = request.headers.get("Origin")
            response.headers["Access-Control-Allow-Origin"] = origin if origin else "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, Accept"
            return response

    # Initialize database schema
    with app.app_context():
        init_db()

    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
