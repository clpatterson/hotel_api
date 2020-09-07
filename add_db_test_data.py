from api import create_app, db
app = create_app('development')
app.app_context().push()
db.drop_all()
db.create_all()

from random import randint
from datetime import datetime, date
from models import Users, Hotels, Rooms, Reservations, RoomInventory
from common.utils import months_out

# Add User data
users = [
    {
        'username': 'Jenny',
        'email': 'jennyfakeemail@mail.com',
        'created_date': datetime.now(),
        'last_modified_date': datetime.now()
    },
    {
        'username': 'Charlie',
        'email': 'charliefakeemail@mail.com',
        'created_date': datetime.now(),
        'last_modified_date': datetime.now()
    }
]

for user in users:
    user = Users(**user)
    user.add_user()
print('Users added.')

# Add hotel data
hotels = [
    {
        'created_date': datetime.now(),
        'last_modified_date': datetime.now(),
        'name': 'The Asteroid',
        'total_double_rooms': 1,
        'total_queen_rooms': 14,
        'total_king_rooms': 7
    },
    {
        'created_date': datetime.now(),
        'last_modified_date': datetime.now(),
        'name': 'The New Asteroid',
        'total_double_rooms': 14,
        'total_queen_rooms': 16,
        'total_king_rooms': 16
    },
    {
        'created_date': datetime.now(),
        'last_modified_date': datetime.now(),
        'name': 'The Luxury Asteroid Hotel',
        'total_double_rooms': 5,
        'total_queen_rooms': 14,
        'total_king_rooms': 11
    }
]

for hotel in hotels:
    new_hotel = Hotels(created_date=hotel['created_date'],
                   last_modified_date=hotel['last_modified_date'],
                   name=hotel['name'])
    new_hotel.add_hotel(total_double_rooms=hotel['total_double_rooms'],
                    total_queen_rooms=hotel['total_queen_rooms'],
                    total_king_rooms=hotel['total_king_rooms'])
print('Hotels added.')

# Add reservation data
reservations = [
    {
    'user_id': 1,
    'checkin_date': date.fromisoformat('2020-09-01'),
    'checkout_date': date.fromisoformat('2020-09-05'),
    'guest_full_name': u'Roger Briggs',
    'desired_room_type': 'double',
    'hotel_id': 2,
    'created_date': datetime.now(),
    'last_modified_date': datetime.now(),
    'is_cancelled': False,
    'is_completed': True
    },
    {
    'user_id': 1,
    'checkin_date': date.fromisoformat('2020-09-02'),
    'checkout_date': date.fromisoformat('2020-09-07'),
    'guest_full_name': u'Miguel Grinberg',
    'desired_room_type': 'queen',
    'hotel_id': 2,
    'created_date': datetime.now(),
    'last_modified_date': datetime.now(),
    'is_cancelled': False,
    'is_completed': True
    },
    {
    'user_id': 1,
    'checkin_date': date.fromisoformat('2020-09-03'),
    'checkout_date': date.fromisoformat('2020-09-08'),
    'guest_full_name': u'Oprah Winfrey',
    'desired_room_type': 'king',
    'hotel_id': 2,
    'created_date': datetime.now(),
    'last_modified_date': datetime.now(),
    'is_cancelled': False,
    'is_completed': True
    }
]

for reservation in reservations:
    db.session.add(Reservations(**reservation))
db.session.commit()
print('Reservations added.')