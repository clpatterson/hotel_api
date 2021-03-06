import pytest

from config import settings
from tests.util import USER_NAME, EMAIL, PASSWORD
from lib.seed_data.seed_data import seed_db
from hotel_api.extensions import db as _db
from hotel_api.app import create_app
from hotel_api.models import Users


@pytest.yield_fixture(scope="session")
def app():
    """
    Setup our flask test app, this only gets executed once.

    :return: Flask app
    """
    _app = create_app(config_name="testing")

    # Establish an application context before running the tests.
    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.yield_fixture(scope="function")
def client(app):
    """
    Setup an app client, this gets executed for each test function.

    :param app: Pytest fixture
    :return: Flask app client
    """
    yield app.test_client()


@pytest.fixture(scope="session")
def db(app):
    """
    Setup our database, this only gets executed once per session.

    :param app: Pytest fixture
    :return: SQLAlchemy database session
    """
    # Ensure schema has been created before creating tables.
    stmt = "CREATE SCHEMA IF NOT EXISTS hotel_api;"
    _db.engine.execute(stmt)

    _db.drop_all()
    _db.create_all()
    print("Database is setup!")

    # Seed database with initial data
    seed_db(test=True)

    return _db


@pytest.fixture(scope="session")
def user(db):
    """
    Setup test user, this gets executed once per session.
    :param db: Pytest db fixture
    :return: Test user
    """
    user = Users(user_name=USER_NAME, email=EMAIL, password=PASSWORD)
    user.add()

    return user