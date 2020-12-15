import os


class Config(object):
    DEBUG = False
    TESTING = False
    SERVER_NAME = "localhost.localdomain:8000"
    SECRET_KEY = "insecurekeyfordev"
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://hotel_api:devpassword@postgres:5432/hotel_api"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SEED_ADMIN_EMAIL = "pattersoncharlesl@gmail.com"
    SEED_ADMIN_PASSWORD = "devadminpassword"


class ProductionConfig(Config):
    SEVER_NAME = os.environ.get("SERVER_NAME")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
    db_uri = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/hotel_api"
    SQLALCHEMY_DATABASE_URI = db_uri


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "{0}_test".format(Config.SQLALCHEMY_DATABASE_URI)


config = {
    "development": DevelopmentConfig(),
    "testing": TestingConfig(),
    "production": ProductionConfig(),
}
