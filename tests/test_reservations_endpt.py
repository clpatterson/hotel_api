from datetime import datetime, timedelta

from flask import url_for


checkin_date = datetime.now().strftime("%Y-%m-%d")
checkout_date = datetime.now() + timedelta(days=5)
checkout_date = checkout_date.strftime("%Y-%m-%d")


class TestReservationList(object):
    def test_reservationList_get(self, client, db):
        """Reservation list endpoint should return 200 and list of all reservations."""
        response = client.get(url_for("reservations"))

        assert response.status_code == 200
        assert len(response.get_json()["reservations"]) == 3
        assert "uri" in response.get_json()["reservations"][0]

    def test_reservationlist_post_valid_reservation(self, client, db):
        """Reservation list should return 200 and reservation details for vaild reservation."""
        data = {
            "checkin_date": checkin_date,
            "checkout_date": checkout_date,
            "guest_full_name": "Charlie Patterson",
            "desired_room_type": "king",
            "hotel_id": 1,
        }
        response = client.post(url_for("reservations"), json=data)

        assert response.status_code == 201
        assert response.get_json()["reservations"]["checkin_date"] == checkin_date
        assert response.get_json()["reservations"]["checkout_date"] == checkout_date

    def test_reservationlist_post_invalid_reservation_dates(self, client, db):
        """Reservation list should return 400 when dates are unavailable."""
        data = {
            "checkin_date": "2020-09-01",
            "checkout_date": "2020-09-05",
            "guest_full_name": "Jim Lately",
            "desired_room_type": "double",
            "hotel_id": 1,
        }
        response = client.post(url_for("reservations"), json=data)

        print(response.get_json())

        assert response.status_code == 400

    def test_reservationlist_post_reservation_missing_param(self, client, db):
        """Reservation list should return 400 reservation is missing params."""
        data = {
            "checkin_date": "2020-09-01",
            "checkout_date": "2020-09-05",
            "guest_full_name": "Jim Lately",
            "desired_room_type": "double",
        }
        response = client.post(url_for("reservations"), json=data)

        print(response.get_json())

        assert response.status_code == 400

    def test_reservationlist_post_reservation_not_available(self, client, db):
        """Reservation list should return 400 if that hotel is already fully booked."""
        data = {
            "checkin_date": checkin_date,
            "checkout_date": checkout_date,
            "guest_full_name": "Charlie Patterson",
            "desired_room_type": "king",
            "hotel_id": 1,
        }

        for i in range(4):  # There are max 3 rooms available in all hotels
            response = client.post(url_for("reservations"), json=data)

        assert response.status_code == 400


class TestReservation(object):
    def test_reservation_get_valid_id(self, client, db):
        """Reservation endpoint should return 200 and data for valid reservation id."""
        response = client.get(url_for("reservation", id=1))

        assert response.status_code == 200
        assert response.get_json()["reservation"]["guest_full_name"] == "Roger Briggs"

    def test_reseration_get_invalid_id(self, client, db):
        """Reservation endpoint should return 404 when supplied invalid reservation id."""
        response = client.get(url_for("reservation", id=3000))

        assert response.status_code == 404

    # TODO: update method for reservations is fucked up. Need to review best way to use SQLAlchemy for this.

    def test_reservation_valid_update(self, client, db):
        """Reservation endpoint should return 201 and updated reservation data for valid update."""
        data = {
            "checkin_date": checkin_date,
            "checkout_date": checkout_date,
            "guest_full_name": "Charlie Patterson",
            "desired_room_type": "double",
            "hotel_id": 1,
        }  # change room type from king to double

        response = client.put(url_for("reservation", id=4), json=data)

        assert response.status_code == 200
        assert response.get_json()["reservation"]["desired_room_type"] == "double"

    def test_reservation_invalid_update(self, client, db):
        """Reservation endpoint should return 400 and error message for invalid update."""
        data = {
            "checkin_date": "2020-09-01",
            "checkout_date": "2020-09-05",
            "guest_full_name": "Charlie Patterson",
            "desired_room_type": "double",
            "hotel_id": 1,
        }  # change dates to invalid range

        response = client.put(url_for("reservation", id=4), json=data)

        assert response.status_code == 400
