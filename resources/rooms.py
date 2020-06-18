from datetime import datetime
from flask import abort
from flask_restful import Resource, reqparse, fields, marshal
from sqlalchemy import func
from models import db, Rooms


room_fields = {
    'id': fields.Integer,
    'type': fields.String,
    'hotel_id': fields.Integer,
    'created_date': fields.DateTime,
    'last_modified_date': fields.DateTime,
    'uri': fields.Url('room')
}

# Parser for HotelList and Hotel resources
reqparse = reqparse.RequestParser()
reqparse.add_argument('hotel_id', type=str, required=False,
                      help="No hotel id for room provided.", location='json')
reqparse.add_argument('type', type=str, required=False,
                      help="No room type provided.", location='json')

class RoomList(Resource):
    def __init__(self):
        self.reqparse = reqparse
        super(RoomList, self).__init__()

    def get(self):
        """List all rooms."""
        rooms = Rooms.get_rooms()
        return {'rooms': [marshal(room, room_fields) for room in rooms]}

    def post(self):
        """Add a new room to rooms list."""
        args = self.reqparse.parse_args()
        room = {
            'hotel_id': args['hotel_id'],
            'type': args['type'],
            'created_date': datetime.now(),
            'last_modified_date': datetime.now()
        }
        room = Rooms(**room)
        room.add_room()
        # handle sqlalchemy Integrity error if parent hotel does not exist
        return {'rooms': marshal(room, room_fields)}, 201


class Room(Resource):
    # def __init__(self):
    #     self.reqparse = reqparse
    #     super(Room, self).__init__()

    def delete(self, id):
        """Delete specified room."""
        Rooms.delete_room(id)
        return {'deleted': True}
