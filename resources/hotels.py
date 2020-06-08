
from datetime import datetime
from flask import abort
from flask_restful import Resource, reqparse, fields, marshal

# TODO: create a postgres database and store these there
hotels = [
    {
    'id': 1,
    'hotel_name': 'The Asteroid',
    'total_double_rooms': 10,
    'total_queen_rooms': 10,
    'total_king_rooms': 10,
    'created_date': u'2020-05-01T14:09:13.702495',
    'last_updated_date': u'2020-05-01T14:09:13.702495'
    }
]

hotel_fields = {
    'id': fields.Integer,
    'hotel_name': fields.String,
    'total_double_rooms': fields.Integer,
    'total_queen_rooms': fields.Integer,
    'total_king_rooms': fields.Integer,
    'created_date' : fields.String,
    'last_updated_date' : fields.String,
    'uri': fields.Url('hotel')
}

# Parser for HotelList and Hotel resources
reqparse = reqparse.RequestParser()
reqparse.add_argument('hotel_name', type = str, required = True,
            help = "No hotel name provided.", location = 'json')
reqparse.add_argument('total_double_rooms', type = int, required = True,
    help = "Total number of double rooms in the hotel not provided.", location = 'json')
reqparse.add_argument('total_queen_rooms', type = int, required = True,
    help = "Total number of queen rooms in the hotel not provided.", location = 'json')
reqparse.add_argument('total_king_rooms', type = int, required = True,
    help = "Total number of king rooms in the hotel not provided.", location = 'json')

class HotelList(Resource):
    def __init__(self):
        self.reqparse = reqparse
        super(HotelList, self).__init__()

    def get(self):
        """List all hotels."""
        return { 'hotels': [marshal(hotel, hotel_fields) for hotel in hotels] }
    
    def post(self):
        """Add a new reservation to the reservations list."""
        args = self.reqparse.parse_args()
        hotel = {
                 'id': hotels[-1]['id'] + 1 if len(hotels) > 0 else 1,
                 'hotel_name': args['hotel_name'],
                 'total_double_rooms': args['total_double_rooms'],
                 'total_queen_rooms': args['total_queen_rooms'],
                 'total_king_rooms': args['total_king_rooms'],
                 'created_date': datetime.now().isoformat(),
                 'last_updated_date': datetime.now().isoformat()
                 }    
        hotels.append(hotel)
        return {'hotels': marshal(hotel, hotel_fields)}, 201

class Hotel(Resource):
    def __init__(self):
        self.reqparse = reqparse
        super(Hotel, self).__init__()
    
    def get(self, id):
        """List specified hotel."""
        hotel = [hotel for hotel in hotels if hotel['id'] == id]
        if len(hotel) == 0:
            abort(404)
        return { 'hotel': marshal(hotel[0], hotel_fields)} 
    
    def put(self, id):
        """Update specified hotel."""
        hotel = [hotel for hotel in hotels if hotel['id'] == id]
        if len(hotel) == 0:
            abort(404)
        hotel = hotel[0]
        args = self.reqparse.parse_args()
        for k,v in args.items():
            if v is not None:
                hotel[k] = v
        hotel['last_updated_date'] = datetime.now().isoformat()
        return { 'hotel': marshal(hotel, hotel_fields)}
    
    def delete(self, id):
        """Delete specified hotel."""
        hotel = [hotel for hotel in hotels if hotel['id'] == id]
        if len(hotel) == 0:
            abort(404)
        hotels.remove(hotel[0])
        return {'deleted': True}
