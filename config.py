import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "ShallNotBeNamed")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.environ.get("FLASK_ENV") != "testing"