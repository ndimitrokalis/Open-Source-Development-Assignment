from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def startup():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    return app