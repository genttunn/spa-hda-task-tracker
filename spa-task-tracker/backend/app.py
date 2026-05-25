import os
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from models import db


def create_app():
    app = Flask(__name__)

    db_path = os.path.join(os.path.dirname(__file__), "tasks.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
        seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 900))
    )

    db.init_app(app)
    JWTManager(app)

    # CORS: explicit origins only — not wildcard.
    # supports_credentials=True is required for non-simple headers (Authorization).
    # Demo: change origins to "*" here and observe the browser reject the response
    # because the spec forbids Access-Control-Allow-Origin: * + Allow-Credentials: true.
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    "http://localhost:5173",
                    "http://127.0.0.1:5173",
                ]
            }
        },
        supports_credentials=True,
    )

    from auth import auth_bp
    from routes.admin import admin_bp
    from routes.tasks import tasks_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(tasks_bp, url_prefix="/api/tasks")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    with app.app_context():
        db.create_all()

    return app


app = create_app()
