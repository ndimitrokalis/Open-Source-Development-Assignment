class Config:
    SECRET_KEY = "ShallNotBeNamed"
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True