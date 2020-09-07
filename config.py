class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True
    # TODO: Store this as env variable
    SQLALCHEMY_DATABASE_URI = 'postgresql://admin:docker@34.68.188.97:5432/hotel_api'

    @staticmethod
    def init_app(app):  # may be useful in customizing config in future
        pass


config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
