from flask import Flask, request
from config import Config
from app.repositories.lead_repository import LeadRepository
from flask_cors import CORS

_CORS_HEADERS = "Content-Type, Authorization, X-Requested-With, Accept"
_CORS_METHODS = "GET, POST, PUT, DELETE, OPTIONS"


def _setup_cors(app: Flask) -> None:
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False,
         allow_headers=_CORS_HEADERS.split(", "), methods=_CORS_METHODS.split(", "))

    @app.after_request
    def _cors_headers(response):
        origin = request.headers.get("Origin")
        response.headers["Access-Control-Allow-Origin"] = origin or "*"
        response.headers["Access-Control-Allow-Methods"] = _CORS_METHODS
        response.headers["Access-Control-Allow-Headers"] = _CORS_HEADERS
        return response

    @app.before_request
    def _preflight():
        if request.method == "OPTIONS":
            resp = app.make_response(("", 204))
            origin = request.headers.get("Origin")
            resp.headers["Access-Control-Allow-Origin"] = origin or "*"
            resp.headers["Access-Control-Allow-Methods"] = _CORS_METHODS
            resp.headers["Access-Control-Allow-Headers"] = _CORS_HEADERS
            return resp


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    _setup_cors(app)

    with app.app_context():
        LeadRepository().init()

    from app.routes import main_bp
    app.register_blueprint(main_bp)
    return app
