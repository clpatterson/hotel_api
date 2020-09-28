# Hotel Reservation System API
## Introduction
This is a simple hotel reservation system REST API for a fictious hotel group,
the Asteroid Group. The Asteroid Group operates hotels on select asteroids in
the solar system. It provides high quality, luxury stays at no cost as well as
transportation to and from asteroids on the latest light speed spacecraft.

The API is built with Flask-Restful and Postgres, deployed using Docker Compose, and tested
using Postman (cli testing using Newman coming soon). The API can be tested
locally by following the steps below:

1. Clone repo locally
```
git clone https://github.com/clpatterson/hotel_api.git
```
2. Start up local development environment in project root directory
```
docker-compose up --build
```
3. Initialize and seed the database with cli command
```
docker-compose exec api hotel_api db reset
```
4. Test endpoints using curl
* See the availble endpoints and methods below. Detailed documentation
is coming soon.

## Resources
The base url for local testing.
```
http://localhost:8000/hotel/api/v1.0/
```

### Hotels
* Hotels are objects representing asteroid hotels operated by the Asteroid
Group.
```json
# Hotel Object
{
    "id": 1,
    "name": "1_Ceres",
    "established_date": "1801-Jan-01",
    "proprietor": "Piazzi, G.",
    "astrd_diameter": 939.4,
    "astrd_surface_composition": "carbonaceous",
    "created_date": "Sun, 27 Sep 2020 21:57:34 -0000",
    "last_modified_date": "Sun, 27 Sep 2020 21:57:34 -0000",
    "total_double_rooms": 10,
    "total_queen_rooms": 14,
    "total_king_rooms": 16,
    "uri": "/hotel/api/v1.0/hotels/1"
}
```
* Hotels endpoints: 
    * ```/hotels```
        * This endpoint can be used to list and create hotel objects.
        * ```GET```: Retrive a list of all hotel objects.
        * ```POST```: Create a new hotel object.
    * ```/hotels/:id```
        * This endpoint can be used to interact with individual hotel object.
        * ```GET```: Retrive a hotel.
        * ```PUT```: Update a hotel.
        * ```DELETE```: Delete a hotel.
    * ```/hotels/availabilities``` (Coming soon)
        * This endpoint can be used to search for hotels with rooms available
        for a given date range. Results can be filtered by passing addition
        parameters such as asteroid size and max travel time (total time it
        takes to travel from Earth to asteroid at light speed in minutes). 

### Reservations
* Reservations are objects representing reservations for asteroid hotel stays.
```json
{
    "checkin_date": "2020-09-02 00:00:00",
    "checkout_date": "2020-09-07 00:00:00",
    "guest_full_name": "Miguel Grinberg",
    "desired_room_type": "queen",
    "hotel_id": 2,
    "created_date": "2020-09-27 21:57:34.329830",
    "last_modified_date": "2020-09-28 15:40:27.803803",
    "is_cancelled": true,
    "is_completed": true,
    "uri": "/hotel/api/v1.0/reservations/2"
}

```
* Reservations endpoints:
    * ```/reservations```
        * This endpoint can be used to list and create reservation objects.
        * ```GET```: Retrive a list of all reservations.
        * ```POST```: Create a new reservation.
    * ```/reservations/:id```
        * This endpoint can be used to interact with single reservation 
        objects.
        * ```GET```: Retrive a reservation.
        * ```PUT```: Update a reservation.
        * ```DELETE```: Delete a reservation.
