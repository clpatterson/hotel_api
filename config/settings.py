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
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")


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
