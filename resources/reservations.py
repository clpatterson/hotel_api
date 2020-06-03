from flask import abort
from flask_restful import Resource, reqparse, fields, marshal

# TODO: create a postgres database and store these there
reservations = [
    {
    'id': 1,
    'checkin_date': u'2020-05-01',
    'checkout_date': u'2020-05-03',
    'guest_full_name': u'Roger Briggs',
    'hotel_id': 1,
    'room_id': 1
    },
    {
    'id': 2,
    'checkin_date': u'2020-05-03',
    'checkout_date': u'2020-05-04',
    'guest_full_name': u'Miguel Grinberg',
    'hotel_id': 1,
    'room_id': 2
    },
    {
    'id': 3,
    'checkin_date': u'2020-05-03',
    'checkout_date': u'2020-05-04',
    'guest_full_name': u'Oprah Winfrey',
    'hotel_id': 1,
    'room_id': 1
    }
]

# for creating public / more manage-able urls
reservation_fields = {
    'checkin_date': fields.String,
    'checkout_date': fields.String,
    'guest_name': fields.String,
    'uri': fields.Url('reservation')
}

class ReservationList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser() # these lines are for input validation
        self.reqparse.add_argument('checkin_date', type = str, required = True,
            help = "No checkin date provided.", location = 'json')
        self.reqparse.add_argument('checkout_date', type = str, required = True,
            help = "No checkout date provided.", location = 'json')
        self.reqparse.add_argument('guest_full_name', type = str, required = True,
            help = "No guest name provided.", location = 'json')
        super(ReservationList, self).__init__()
    
    def get(self):
        """List all reservations."""
        return { 'reservations': [marshal(reservation, reservation_fields) for reservation in reservations] }
    
    def post(self):
        """Add a new reservation to the reservations list."""
        args = self.reqparse.parse_args()
        reservation = {
                        'id': reservations[-1]['id'] + 1 if len(reservations) > 0 else 1,
                        'checkin_date': args['checkin_date'],
                        'checkout_date': args['checkout_date'],
                        'guest_full_name': args['guest_full_name'],
                        'hotel_id': 1,
                        'room_id': 1 # ToDo: Query inventory and assign
                       }
        reservations.append(reservation)
        return {'reservations': marshal(reservation, reservation_fields)}, 201

class Reservation(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser() # these lines are for input validation
        self.reqparse.add_argument('checkin_date', type = str,
            help = "No checkin date provided.", location = 'json')
        self.reqparse.add_argument('checkout_date', type = str,
           help = "No checkout date provided.", location = 'json')
        self.reqparse.add_argument('guest_full_name', type = str,
           help = "No guest name provided.", location = 'json')
        super(Reservation, self).__init__()
    
    def get(self, id):
        """List specified reservation."""
        reservation = [res for res in reservations if res['id'] == id]
        if len(reservation) == 0:
            abort(404)
        return { 'reservation': marshal(reservation[0], reservation_fields)} 
    
    def put(self, id):
        """Update specified reservation."""
        reservation = [res for res in reservations if res['id'] == id]
        if len(reservation) == 0:
            abort(404)
        reservation = reservation[0]
        args = self.reqparse.parse_args()
        for k,v in args.items():
            if v is not None:
                reservation[k] = v
        return { 'reservation': marshal(reservation, reservation_fields)}
    
    def delete(self, id):
        """Delete specified reservation."""
        reservation = [res for res in reservations if res['id'] == id]
        if len(reservation) == 0:
            abort(404)
        reservations.remove(reservation[0])
        return {'result': True}