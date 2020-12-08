from datetime import datetime, date
from random import randint

from hotel_api.models import Users, Hotels, Rooms, Reservations, RoomInventory
from hotel_api.extensions import db
from lib.util_datetime import months_out
from lib.astrd_data.astrd_data import astrd_data


#  Test users
users = [
    {
        "user_name": "roger_briggs",
        "password": "rogerpassword",
        "email": "roger.briggs@email.com",
    },
    {
        "user_name": "miguel_grinberg",
        "password": "miguelpassword",
        "email": "miguel.grinberg@email.com",
    },
    {
        "user_name": "oprah_winfrey",
        "password": "oprahpassword",
        "email": "oprah.winfrey@email.com",
    },
    {
        "user_name": "charlie_patterson",
        "password": "charliepassword",
        "email": "charlie.patterson@email.com",
    },
]

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


# Test reservation data
reservations = [
    {
        "checkin_date": date.fromisoformat("2020-09-01"),
        "checkout_date": date.fromisoformat("2020-09-05"),
        "guest_full_name": u"Roger Briggs",
        "desired_room_type": "double",
        "customer_user_id": 1,
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
        "customer_user_id": 2,
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
        "customer_user_id": 3,
        "desired_room_type": "king",
        "hotel_id": 2,
        "created_date": datetime.now(),
        "last_modified_date": datetime.now(),
        "is_cancelled": False,
        "is_completed": True,
    },
]


def seed_db(test=False, dev=False):
    """Seed database with test or initial data."""
    # Seed hotels
    hotels = get_hotels()
    for hotel in hotels:
        new_hotel = Hotels(**hotel)
        if test:
            new_hotel.add_hotel(
                total_double_rooms=3,
                total_queen_rooms=3,
                total_king_rooms=3,
                inv_months=1,
            )

        else:  # Seed larger hotels for prod
            new_hotel.add_hotel(
                total_double_rooms=randint(1, 25),
                total_queen_rooms=randint(1, 25),
                total_king_rooms=randint(1, 25),
            )

    # Seed users and reservations for testing
    if test or dev:
        for user in users:
            user = Users(**user)
            if "charlie_patterson" == user.user_name:
                user.add(admin=True)
            else:
                user.add()

        for reservation in reservations:
            db.session.add(Reservations(**reservation))
            db.session.commit()

    # Seed only admin user for prod
    else:
        from instance.settings import SEED_ADMIN_EMAIL, SEED_ADMIN_PASSWORD

        user["user_name"] = "admin"
        user["password"] = SEED_ADMIN_PASSWORD
        user["email"] = SEED_ADMIN_EMAIL

        user = Users(**user)
        user.add()

    return None