from datetime import datetime, date
from random import randint

from hotel_api.models import Hotels, Rooms, Reservations, RoomInventory
from hotel_api.extensions import db
from lib.util_datetime import months_out
from lib.astrd_data.astrd_data import astrd_data

# Initial 54 asteroid hotels
def get_hotels():
    """Return list of first 54 asteroid hotels."""
    hotels = []
    for astrd in astrd_data.keys():
        hotel = {
            "created_date": datetime.now(),
            "last_modified_date": datetime.now(),
            "name": astrd.replace(" ", "_"),
        }
        hotel.update(astrd_data[astrd])
        hotels.append(hotel)
    return hotels


# Initial reservation data
reservations = [
    {
        "checkin_date": date.fromisoformat("2020-09-01"),
        "checkout_date": date.fromisoformat("2020-09-05"),
        "guest_full_name": u"Roger Briggs",
        "desired_room_type": "double",
        "hotel_id": 2,
        "created_date": datetime.now(),
        "last_modified_date": datetime.now(),
        "is_cancelled": False,
        "is_completed": True,
    },
    {
        "checkin_date": date.fromisoformat("2020-09-02"),
        "checkout_date": date.fromisoformat("2020-09-07"),
        "guest_full_name": u"Miguel Grinberg",
        "desired_room_type": "queen",
        "hotel_id": 2,
        "created_date": datetime.now(),
        "last_modified_date": datetime.now(),
        "is_cancelled": False,
        "is_completed": True,
    },
    {
        "checkin_date": date.fromisoformat("2020-09-03"),
        "checkout_date": date.fromisoformat("2020-09-08"),
        "guest_full_name": u"Oprah Winfrey",
        "desired_room_type": "king",
        "hotel_id": 2,
        "created_date": datetime.now(),
        "last_modified_date": datetime.now(),
        "is_cancelled": False,
        "is_completed": True,
    },
]


def seed_db(test=False):
    """Seed database with initial data."""
    # Seed Hotels
    hotels = get_hotels()
    for hotel in hotels:
        new_hotel = Hotels(**hotel)
        if test:
            new_hotel.add_hotel(
                total_double_rooms=randint(1, 3),
                total_queen_rooms=randint(1, 3),
                total_king_rooms=randint(1, 3),
                inv_months=1,
            )
        else:
            new_hotel.add_hotel(
                total_double_rooms=randint(1, 25),
                total_queen_rooms=randint(1, 25),
                total_king_rooms=randint(1, 25),
            )

    # Seed Reservations
    for reservation in reservations:
        db.session.add(Reservations(**reservation))
        db.session.commit()

    return None