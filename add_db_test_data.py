from api import create_app, db
app = create_app('development')
app.app_context().push()
db.drop_all()
db.create_all()

from random import randrange
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
    db.session.add(Users(**user))
db.session.commit()
print('Users added.')

# Add hotel data
hotels = [
    {
        'name': 'The Asteroid',
         'created_date': datetime.now(),
         'last_modified_date': datetime.now()
    },
    {
        'name': 'The New Asteroid',
         'created_date': datetime.now(),
         'last_modified_date': datetime.now()
    },
    {
        'name': 'The Luxury Asteroid Hotel',
         'created_date': datetime.now(),
         'last_modified_date': datetime.now()
    }
]

hotel_ids = []
for hotel in hotels:
    hotel = Hotels(**hotel)
    db.session.add(hotel)
    db.session.flush()
    hotel_ids.append(hotel.__dict__['id'])
db.session.commit()
print('Hotels added.')

# Add hotel room data
def add_hotel_rooms(hotel_id):
    """Add a random number of rooms for each room type."""
    rooms = []
    for double in range(randrange(1,20)):
        room = Rooms(type='double', hotel_id=hotel_id, created_date=datetime.now(), last_modified_date=datetime.now())
        rooms.append(room)
    for queen in range(randrange(1,20)):
        room = Rooms(type='queen', hotel_id=hotel_id, created_date=datetime.now(), last_modified_date=datetime.now())
        rooms.append(room)
    for king in range(randrange(1,20)):
        room = Rooms(type='king', hotel_id=hotel_id, created_date=datetime.now(), last_modified_date=datetime.now())
        rooms.append(room)
    db.session.add_all(rooms)
    db.session.flush()
    db.session.commit()
    room_id_array = [room.id for room in rooms]
    return room_id_array

for hotel_id in hotel_ids:
    rooms = add_hotel_rooms(hotel_id)
    print(f"rooms added for hotel {hotel_id}")
    RoomInventory.bulk_add_inventory(hotel_id=hotel_id, 
                                     room_id_array=rooms, 
                                     start_date=date.today(),
                                     end_date=months_out(date.today(),6))
    print(f"room inventory added for hotel {hotel_id}")
    
print('Hotel rooms added.')

# Add reservation data
reservations = [
    {
    'user_id': 1,
    'checkin_date': date.fromisoformat('2020-05-01'),
    'checkout_date': date.fromisoformat('2020-05-05'),
    'guest_full_name': u'Roger Briggs',
    'hotel_id': 2,
    'created_date': datetime.now(),
    'last_modified_date': datetime.now(),
    'is_cancelled': False,
    'is_completed': True
    },
    {
    'user_id': 1,
    'checkin_date': date.fromisoformat('2020-05-02'),
    'checkout_date': date.fromisoformat('2020-05-07'),
    'guest_full_name': u'Miguel Grinberg',
    'hotel_id': 2,
    'created_date': datetime.now(),
    'last_modified_date': datetime.now(),
    'is_cancelled': False,
    'is_completed': True
    },
    {
    'user_id': 1,
    'checkin_date': date.fromisoformat('2020-05-03'),
    'checkout_date': date.fromisoformat('2020-05-08'),
    'guest_full_name': u'Oprah Winfrey',
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
# TODO: Generate room inventory for 6 months out