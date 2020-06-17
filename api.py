from flask import Flask
from flask_restful import Api

from config import config
from models import db


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])  # load config from file
    config[config_name].init_app(app)
    # Configure and instantiate the database engine
    db.init_app(app)
    api = Api(app)

    from resources.reservations import ReservationList, Reservation
    from resources.hotels import HotelList, Hotel
    from resources.users import UserList, User

    # Register the routes for resources available through the api
    api.add_resource(ReservationList, '/hotel/api/v1.0/reservations',
                     endpoint='reservations')
    api.add_resource(Reservation, '/hotel/api/v1.0/reservations/<int:id>',
                     endpoint='reservation')
    api.add_resource(HotelList, '/hotel/api/v1.0/hotels',
                     endpoint='hotels')
    api.add_resource(Hotel, '/hotel/api/v1.0/hotels/<int:id>',
                     endpoint='hotel')
    api.add_resource(UserList, '/hotel/api/v1.0/users',
                     endpoint='users')
    api.add_resource(User, '/hotel/api/v1.0/users/<int:id>',
                     endpoint='user')
    return app


if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True)
