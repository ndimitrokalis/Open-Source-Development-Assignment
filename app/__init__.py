from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def startup():
    app = Flask(__name__)
    app.config.from_object("config.Config")
 
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
 
    from .models.user import User
 
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
 
    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
 
    with app.app_context():
        db.create_all()
 
    return app