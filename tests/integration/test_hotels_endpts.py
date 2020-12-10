from flask import url_for


class TestHotelList(object):
    def test_hotellist_get(self, client, db):
        """
        Hotels endpoint should return a list of all hotels and
        200 status code.
        """
        response = client.get(url_for("api.hotels"))

        assert response.status_code == 200

    def test_hotellist_create_hotel_valid_input(self, client, db):
        """
        Hotels endpoint should create hotel for vaild input.
        """
        data = {
            "name": "Bigasteroid",
            "ephem_data": "some fake ephem data",
            "established_date": "1779-Jan-01",
            "proprietor": "Patterson, C.",
            "astrd_diameter": 85.2,
            "astrd_surface_composition": "carbonaceous",
            "total_double_rooms": 3,
            "total_queen_rooms": 3,
            "total_king_rooms": 3,
        }

        response = client.post(url_for("api.hotels"), json=data)

        assert response.status_code == 201
        assert "name" in response.get_json().keys()

    def test_hotellist_create_hotel_duplicate(self, client, db):
        """
        Hotels endpoint should fail and return message when new hotel already exists.
        """
        data = {
            "name": "Bigasteroid",
            "ephem_data": "some fake ephem data",
            "established_date": "1779-Jan-01",
            "proprietor": "Patterson, C.",
            "astrd_diameter": 85.2,
            "astrd_surface_composition": "carbonaceous",
            "total_double_rooms": 3,
            "total_queen_rooms": 3,
            "total_king_rooms": 3,
        }

        response = client.post(url_for("api.hotels"), json=data)

        assert response.status_code == 400
        assert "Hotel already exists." in response.get_json()["message"]

    def test_hotellist_create_hotel_missing_name(self, client, db):
        """
        Hotels endpoint should fail and return message when all required
        fields are not present.
        """
        data = {
            "ephem_data": "some fake ephem data",
            "established_date": "1779-Jan-01",
            "proprietor": "Patterson, C.",
            "astrd_diameter": 85.2,
            "astrd_surface_composition": "carbonaceous",
            "total_double_rooms": 3,
            "total_queen_rooms": 3,
            "total_king_rooms": 3,
        }

        response = client.post(url_for("api.hotels"), json=data)

        assert response.status_code == 400
        assert "No hotel name provided." in response.get_json()["errors"]["name"]


class TestHotel(object):
    def test_hotel_get(self, client, db):
        """Hotel endpoint should return hotel data for valid id. """
        response = client.get(url_for("api.hotel", id=1))

        assert response.status_code == 200
        assert "name" in response.get_json()

    def test_hotel_get_invalid_hotel_id(self, client, db):
        """Hotel endpoint should return hotel data for valid id. """
        response = client.get(url_for("api.hotel", id=3000))

        assert response.status_code == 404

    def test_hotel_valid_update(self, client, db):
        """Hotel endpoint should return 200 and updated hotel data for valid update."""
        # Change number of rooms from to 10 for each type
        data = {
            "name": "1_Ceres",
            "established_date": "1801-Jan-01",
            "proprietor": "Piazzi, G.",
            "astrd_diameter": 939.4,
            "astrd_surface_composition": "carbonaceous",
            "total_double_rooms": 10,
            "total_queen_rooms": 10,
            "total_king_rooms": 10,
        }

        response = client.put(url_for("api.hotel", id=1), json=data)

        assert response.status_code == 200
        assert response.get_json()["total_double_rooms"] == 10

    def test_hotel_invalid_update_lowering_room_count(self, client, db):
        """Hotel endpoint should return 200 and updated hotel data for valid update."""
        # Change total number of double rooms to 9
        data = {
            "name": "1_Ceres",
            "established_date": "1801-Jan-01",
            "proprietor": "Piazzi, G.",
            "astrd_diameter": 939.4,
            "astrd_surface_composition": "carbonaceous",
            "total_double_rooms": 9,
            "total_queen_rooms": 10,
            "total_king_rooms": 10,
        }

        response = client.put(url_for("api.hotel", id=1), json=data)

        assert response.status_code == 400
        assert "Hotel room counts cannot shrink." in response.get_json()["message"]

    def test_hotel_update_missing_param(self, client, db):
        """Hotel endpoint should return 200 and updated hotel data for valid update."""
        # Missing total double rooms param
        data = {
            "name": "1_Ceres",
            "established_date": "1801-Jan-01",
            "proprietor": "Piazzi, G.",
            "astrd_diameter": 939.4,
            "astrd_surface_composition": "carbonaceous",
            "total_queen_rooms": 3,
            "total_king_rooms": 2,
        }

        response = client.put(url_for("api.hotel", id=1), json=data)

        assert response.status_code == 400

    def test_hotel_delete_valid_hotel(self, client, db):
        """Hotel endpoint should return 200 and message confirming deletion."""
        response = client.delete(url_for("api.hotel", id=54))

        assert response.status_code == 200

    def test_hotel_delete_invalid_hotel(self, client, db):
        """Hotel endpoint should return 404."""
        response = client.delete(url_for("api.hotel", id=54))

        assert response.status_code == 404
