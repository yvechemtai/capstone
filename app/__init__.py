# Import necessary modules and classes

# app/__init__.py
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_apscheduler import APScheduler
from .config.config import config

# Initialize Flask app and extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
csrf = CSRFProtect()
schedule = APScheduler()

def create_app():
    app = Flask(__name__, template_folder='./templates', static_folder='./static')

    # Load configuration settings
    app.config.from_object(config['development'])

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints and start scheduler
    from app.views.auth_routes import auth
    from app.views.dashboard_routes import home
    from app.views.user_routes import users
    from app.views.loan_routes import loans
    from app.views.contribution_routes import contribution
    from app.views.reminders_routes import reminder
    from app.views.meeting_routes import meetings
    from app.views.settings_routes import settings
    app.register_blueprint(auth)
    app.register_blueprint(home)
    app.register_blueprint(users)
    app.register_blueprint(loans)
    app.register_blueprint(contribution)
    app.register_blueprint(reminder)
    app.register_blueprint(meetings)
    app.register_blueprint(settings)

    schedule.init_app(app)
    schedule.start()

    # Create database tables and perform initial setup
    with app.app_context():
        from app.utils.setup import (
            add_admin_role, 
            add_admin_user, 
            verify_admin_user, 
            add_loan_types, 
            add_loan_durations
            )
        
        db.create_all()
        add_admin_role()
        add_admin_user()
        verify_admin_user()
        add_loan_types()
        add_loan_durations()

    return app
