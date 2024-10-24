import pytest

from config import TestConfig
from app import create_app, db


@pytest.fixture()
def app():
    app = create_app(config_class=TestConfig)
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()
