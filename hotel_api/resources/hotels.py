from datetime import datetime, date

from flask_restx import Namespace, Resource, reqparse, fields, marshal

from hotel_api.models import db, Hotels
from lib.util_datetime import months_out

hotels_ns = Namespace("hotels")

hotel_fields = hotels_ns.model(
    "hotels",
    {
        "name": fields.String(example="1_Ceres"),
        "established_date": fields.String(example="1801-Jan-01"),
        "proprietor": fields.String(example="Piazzi, G."),
        "astrd_diameter": fields.Float(example="939.4"),
        "astrd_surface_composition": fields.String(example="carbonaceous"),
        "created_date": fields.DateTime(example="2020-12-01T01:59:39.297892"),
        "last_modified_date": fields.DateTime(example="2020-12-01T01:59:39.297904"),
        "total_double_rooms": fields.Integer(example=6),
        "total_queen_rooms": fields.Integer(example=4),
        "total_king_rooms": fields.Integer(example=21),
        "uri": fields.Url("hotel", example="/hotels/1"),
    },
)

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
    def __init__(self, *args, **kwargs):
        self.reqparse = reqparse
        super(HotelList, self).__init__(*args, **kwargs)

    @hotels_ns.marshal_with(hotel_fields)
    def get(self):
        """List all hotels."""
        hotels = Hotels.get_hotels()
        return hotels["fields"]

    @hotels_ns.expect(reqparse)
    @hotels_ns.marshal_with(hotel_fields, code=201)
    def post(self):
        """Add a new hotel."""
        args = self.reqparse.parse_args()
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
        new_hotel = dict(new_hotel.__dict__, **hotel_rooms)
        return new_hotel, 201


class Hotel(Resource):
    def __init__(self, *args, **kwargs):
        self.reqparse = reqparse
        super(Hotel, self).__init__(*args, **kwargs)

    @hotels_ns.marshal_with(hotel_fields)
    def get(self, id):
        """List specified hotel."""
        hotel = Hotels.get_hotel(id)
        return hotel["fields"]

    @hotels_ns.expect(reqparse)
    @hotels_ns.marshal_with(hotel_fields)
    def put(self, id):
        """Update specified hotel."""
        self.reqparse.replace_argument("ephem_data", required=False, location="json")
        args = self.reqparse.parse_args()
        hotel = Hotels.update_hotel(id, args)
        return hotel["fields"]

    @hotels_ns.response(200, '{"deleted": True}')
    def delete(self, id):
        """Delete specified hotel."""
        Hotels.delete_hotel(id)
        return {"deleted": True}


hotels_ns.add_resource(HotelList, "", endpoint="hotels")
hotels_ns.add_resource(Hotel, "/<int:id>", endpoint="hotel")