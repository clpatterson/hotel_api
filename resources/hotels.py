from datetime import datetime
from flask import abort
from flask_restful import Resource, reqparse, fields, marshal
from sqlalchemy import func
from models import db, Hotels, Rooms


hotel_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'created_date': fields.DateTime,
    'last_modified_date': fields.DateTime,
    'total_double_rooms': fields.Integer,
    'total_queen_rooms': fields.Integer,
    'total_king_rooms': fields.Integer,
    'uri': fields.Url('hotel')
}

# Parser for HotelList and Hotel resources
reqparse = reqparse.RequestParser()
reqparse.add_argument('name', type=str, required=True,
                      help="No hotel name provided.", location='json')

class HotelList(Resource):
    def __init__(self):
        self.reqparse = reqparse
        super(HotelList, self).__init__()

    def get(self):
        """List all hotels."""
        hotels = Hotels.get_hotels()
        return {'hotels': [marshal(hotel, hotel_fields) for hotel in hotels]}

    def post(self):
        """Add a new hotel to the hotel list."""
        args = self.reqparse.parse_args()
        hotel = {
            'name': args['name'],
            'created_date': datetime.now(),
            'last_modified_date': datetime.now()
        }
        hotel = Hotels(**hotel)
        hotel.add_hotel()
        # TODO: handle errors when hotel already exists
        return {'hotels': marshal(hotel, hotel_fields)}, 201


class Hotel(Resource):
    def __init__(self):
        self.reqparse = reqparse
        super(Hotel, self).__init__()

    def get(self, id):
        """List specified hotel."""
        hotel = Hotels.get_hotel(id)
        return {'hotel': marshal(hotel, hotel_fields)}

    def put(self, id):
        """Update specified hotel."""
        args = self.reqparse.parse_args()
        hotel = Hotels.update_hotel(id, args)
        return {'hotel': marshal(hotel, hotel_fields)}

    def delete(self, id):
        """Delete specified hotel."""
        Hotels.delete_hotel(id)
        return {'deleted': True}
