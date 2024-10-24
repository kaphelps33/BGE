import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"  # In-memory SQLite for fast testing
    SQLALCHEMY_TRACK_MODIFICATIONS = False
