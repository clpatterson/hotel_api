from datetime import datetime, date
from flask_restful import Resource, reqparse, fields, marshal
from hotel_api.models import db, Hotels
from lib.util_datetime import months_out


hotel_fields = {
    "name": fields.String,
    "established_date": fields.String,
    "proprietor": fields.String,
    "astrd_diameter": fields.Float,
    "astrd_surface_composition": fields.String,
    "created_date": fields.DateTime,
    "last_modified_date": fields.DateTime,
    "total_double_rooms": fields.Integer,
    "total_queen_rooms": fields.Integer,
    "total_king_rooms": fields.Integer,
    "uri": fields.Url("hotel"),
}


# Parser for HotelList resources
reqparse = reqparse.RequestParser()
reqparse.add_argument(
    "name", type=str, required=True, help="No hotel name provided.", location="json"
)
reqparse.add_argument(
    "ephem_data",
    type=str,
    required=True,
    help="No ephem_data provided.",
    location="json",
)
reqparse.add_argument(
    "established_date",
    type=str,
    required=True,
    help="No established date provided.",
    location="json",
)
reqparse.add_argument(
    "proprietor",
    type=str,
    required=True,
    help="No proprietor provided.",
    location="json",
)
reqparse.add_argument(
    "astrd_diameter",
    type=float,
    required=True,
    help="No ephem_data provided.",
    location="json",
)
reqparse.add_argument(
    "astrd_surface_composition",
    type=str,
    required=True,
    help="No ephem_data provided.",
    location="json",
)
reqparse.add_argument(
    "total_double_rooms",
    type=int,
    required=True,
    help="Total number of double rooms in the hotel not provided.",
    location="json",
)
reqparse.add_argument(
    "total_queen_rooms",
    type=int,
    required=True,
    help="Total number of queen rooms in the hotel not provided.",
    location="json",
)
reqparse.add_argument(
    "total_king_rooms",
    type=int,
    required=True,
    help="Total number of king rooms in the hotel not provided.",
    location="json",
)


class HotelList(Resource):
    def __init__(self):
        self.reqparse = reqparse
        super(HotelList, self).__init__()

    def get(self):
        """List all hotels."""
        hotels = Hotels.get_hotels()
        return {"hotels": [marshal(hotel, hotel_fields) for hotel in hotels["fields"]]}

    def post(self):
        """Add a new hotel to the hotel reservation system."""
        args = self.reqparse.parse_args()
        # TODO: Handle errors when trying to make same hotel
        hotel = {
            "name": args["name"],
            "ephem_data": args["ephem_data"],
            "established_date": args["established_date"],
            "proprietor": args["proprietor"],
            "astrd_diameter": args["astrd_diameter"],
            "astrd_surface_composition": args["astrd_surface_composition"],
            "created_date": datetime.now(),
            "last_modified_date": datetime.now(),
        }
        hotel_rooms = {
            "total_double_rooms": args["total_double_rooms"],
            "total_queen_rooms": args["total_queen_rooms"],
            "total_king_rooms": args["total_king_rooms"],
        }
        new_hotel = Hotels(**hotel)
        new_hotel.add_hotel(**hotel_rooms)
        hotel = dict(new_hotel.__dict__, **hotel_rooms)
        # TODO: handle errors when hotel already exists (i.e. name is not unique)
        return {"hotels": marshal(hotel, hotel_fields)}


class Hotel(Resource):
    def __init__(self):
        self.reqparse = reqparse
        super(Hotel, self).__init__()

    def get(self, id):
        """List specified hotel."""
        hotel = Hotels.get_hotel(id)
        return {"hotel": marshal(hotel["fields"], hotel_fields)}

    def put(self, id):
        """Update specified hotel."""
        args = self.reqparse.parse_args()
        hotel = Hotels.update_hotel(id, args)
        return {"hotel": marshal(hotel["fields"], hotel_fields)}

    def delete(self, id):
        """Delete specified hotel."""
        Hotels.delete_hotel(id)
        return {"deleted": True}
