from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from models import db
from resources.reservations import ReservationList, Reservation
from resources.hotels import HotelList, Hotel
from resources.users import UserList, User


app = Flask(__name__)
# Configure and instantiate the database engine
# TODO: put these configuration in a file and set an environment variable to 
#  point to them (see flask docs for explanation.)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:docker@34.68.188.97:5432/hotel_api'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)

# Import models after creating db to avoid import error
#from models import db

# interactive python 
# from api import db
# db.create_all()


# Register the routes for resources available through the api
api.add_resource(ReservationList, '/hotel/api/v1.0/reservations', 
                 endpoint ='reservations')
api.add_resource(Reservation, '/hotel/api/v1.0/reservations/<int:id>', 
                 endpoint = 'reservation')
api.add_resource(HotelList, '/hotel/api/v1.0/hotels', 
                 endpoint = 'hotels')
api.add_resource(Hotel, '/hotel/api/v1.0/hotels/<int:id>', 
                 endpoint = 'hotel')
api.add_resource(UserList, '/hotel/api/v1.0/users', 
                 endpoint = 'users')
api.add_resource(User, '/hotel/api/v1.0/users/<int:id>', 
                 endpoint = 'user')

if __name__ == '__main__':
    app.run(debug=True)
