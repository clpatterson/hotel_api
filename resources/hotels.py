from datetime import datetime
from flask import abort
from flask_restful import Resource, reqparse, fields, marshal
from sqlalchemy import func
from models import db, Hotels, Rooms

# TODO: create a postgres database and store these there
hotels = [
    {
        'id': 1,
        'name': 'The Asteroid',
        'created_date': u'2020-05-01T14:09:13.702495',
        # 'last_updated_date': u'2020-05-01T14:09:13.702495'
    }
]

hotel_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'created_date': fields.DateTime,
    'last_updated_date': fields.DateTime,
    'total_double_rooms': fields.Integer,
    'total_queen_rooms': fields.Integer,
    'total_king_rooms': fields.Integer,
    'uri': fields.Url('hotel')
}

# Parser for HotelList and Hotel resources
reqparse = reqparse.RequestParser()
reqparse.add_argument('name', type=str, required=True,
                      help="No hotel name provided.", location='json')
reqparse.add_argument('total_double_rooms', type=int, required=True,
                      help="Total number of double rooms in the hotel not provided.", location='json')
reqparse.add_argument('total_queen_rooms', type=int, required=True,
                      help="Total number of queen rooms in the hotel not provided.", location='json')
reqparse.add_argument('total_king_rooms', type=int, required=True,
                      help="Total number of king rooms in the hotel not provided.", location='json')


class HotelList(Resource):
    def __init__(self):
        self.reqparse = reqparse
        super(HotelList, self).__init__()

    def get(self):
        """List all hotels."""
        hotels = Hotels.get_hotels()
        # hotels = Hotels.query.all()
        # hotels = get_hotel_data(hotels)
        return {'hotels': [marshal(hotel, hotel_fields) for hotel in hotels]}

    def post(self):
        """Add a new reservation to the reservations list."""
        # TODO: prevent the creation of hotels with no rooms
        args = self.reqparse.parse_args()
        hotel = {
            'name': args['name'],
            'created_date': datetime.now().isoformat(),
            # 'last_updated_date': datetime.now()
        }
        hotel = Hotels(**hotel)
        hotel.add_hotel(args['total_double_rooms'],
                        args['total_queen_rooms'],
                        args['total_king_rooms'])
        # TODO: handle errors when hotel already exists
        return {'hotels': marshal(hotel, hotel_fields)}, 201


class Hotel(Resource):
    def __init__(self):
        self.reqparse = reqparse
        super(Hotel, self).__init__()

    def get(self, id):
        """List specified hotel."""
        hotel = Hotels.get_hotel(id)
        # hotel = Hotels.query.get_or_404(id)
        # hotel = get_hotel_data([hotel])
        return {'hotel': marshal(hotel, hotel_fields)}

    def put(self, id):
        """Update specified hotel."""
        # TODO: Steps:
        # 1) check that specified hotel exists in db
        # 2) if no, 404
        # 3) query rooms table for room counts
        # 4) compare request args to room counts in db
        # 5) if room count change, delete or add rooms
        # 6) if room counts same, but name is different, change name
        # 7) commit change
        # 8) package response
        # this performs query with all params
        # hotel = Hotels.query.get_or_404(id)
        # TODO: add error handling if someone renames hotel with non-unique name (use try)
        # hotel = get_hotel_data([hotel])
        # hotel = [hotel for hotel in hotels if hotel['id'] == id]
        # if len(hotel) == 0:
        #     abort(404)
        hotel = Hotels.get_hotel(id)
        hotel = hotel[0]
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v is not None:
                hotel[k] = v
        hotel['last_updated_date'] = datetime.now()
        # TODO: update date
        return {'hotel': marshal(hotel, hotel_fields)}

    def delete(self, id):
        """Delete specified hotel."""
        # TODO: Steps:
        # 1) if hotel doesn't exist in db, 404
        # 2) delete and prepare delete message
        hotel = [hotel for hotel in hotels if hotel['id'] == id]
        if len(hotel) == 0:
            abort(404)
        hotels.remove(hotel[0])
        return {'deleted': True}
