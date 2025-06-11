# app/__init__.py
import os
from flask import Flask
from flask_socketio import SocketIO
from flask_login import LoginManager
from config.settings import Config
from.audit import app_logger # Assuming app_logger is correctly defined in app.audit

socketio = SocketIO()
login_manager = LoginManager()

def create_app():
    # Determine the absolute path to the 'app' directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    # Determine the project root directory (one level up from 'app' directory)
    project_root = os.path.dirname(app_dir)
    # Construct the absolute path to the 'templates' folder in the project root
    template_folder_path = os.path.join(project_root, 'templates')

    app = Flask(__name__, template_folder=template_folder_path) # Explicitly set template_folder
    app.config.from_object(Config)

    app_logger.info("Flask App Initializing...")
    app_logger.info(f"SECRET_KEY {'is set' if Config.SECRET_KEY else 'is NOT set (CRITICAL FOR SECURITY)'}")
    app_logger.info(f"AWS_DEFAULT_REGION: {Config.AWS_DEFAULT_REGION}")
    app_logger.info(f"BEDROCK_PROMPT_ARN: {Config.BEDROCK_PROMPT_ARN}")
    app_logger.info(f"Template folder set to: {template_folder_path}") # For debugging

    socketio.init_app(app, cors_allowed_origins="*") # Adjust cors_allowed_origins for production
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' # Route name for the login page

    from.auth import auth_bp
    app.register_blueprint(auth_bp)

    from.main import main_bp
    app.register_blueprint(main_bp)
    
    from.models import User # Import User model

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    app_logger.info("Flask App Initialized Successfully.")
    return app