from datetime import datetime, timedelta

from flask import url_for

checkin_date = datetime.now().strftime("%Y-%m-%d")
checkout_date = datetime.now() + timedelta(days=5)
checkout_date = checkout_date.strftime("%Y-%m-%d")


class TestAvailabilities(object):
    def test_availabilities_for_valid_input(self, client, db):
        """
        Availabilities endpoint should return 200 status code and
        json response.
        """
        response = client.get(
            url_for("availabilities")
            + f"?checkin={checkin_date}"
            + f"&checkout={checkout_date}"
        )
        json_response = response.get_json()

        assert response.status_code == 200
        assert "name" in json_response[0]

    def test_availabilities_for_multiple_surface_types(self, client, db):
        """
        Availabilities endpoint should return 200 for multiple
        surface types in query string.
        """
        response = client.get(
            url_for("availabilities")
            + f"?checkin={checkin_date}"
            + f"&checkout={checkout_date}"
            + "&surface_type=silicaceous"
            + "&surface_type=carbonaceous"
        )

        assert response.status_code == 200

    def test_availabilities_for_multiple_hotel_names(self, client, db):
        """
        Availabilities endpoint should return 200 for multiple hotel names
        in query string.
        """

        response = client.get(
            url_for("availabilities")
            + f"?checkin={checkin_date}"
            + f"&checkout={checkout_date}"
            + "&name=1_Ceres"
            + "&name=8_Flora"
        )

        assert response.status_code == 200

    def test_availabilities_for_multiple_room_types(self, client, db):
        """
        Availabilities endpoint should return 200 for multiple room types
        in query string.
        """

        response = client.get(
            url_for("availabilities")
            + f"?checkin={checkin_date}"
            + f"&checkout={checkout_date}"
            + "&room_type=king"
            + "&room_type=double"
        )

        assert response.status_code == 200

    def test_availabilities_for_invalid_room_type(self, client, db):
        """
        Availabilities endpoint should return 400 for invalid room_type
        in query string.
        """

        response = client.get(
            url_for("availabilities")
            + f"?checkin={checkin_date}"
            + f"&checkout={checkout_date}"
            + "&room_type=king"
            + "&room_type=cool_room"
        )

        assert response.status_code == 400

    def test_availabilities_for_invalid_surface_type(self, client, db):
        """
        Availabilities endpoint should return 400 for invalid
        surface types in query string.
        """

        response = client.get(
            url_for("availabilities")
            + f"?checkin={checkin_date}"
            + f"&checkout={checkout_date}"
            + "&surface_type=dirty"
            + "&surface_type=carbonaceous"
        )

        assert response.status_code == 400

    def test_availabilities_for_missing_dates(self, client, db):
        """
        Availabilities endpoint should return 400 when no checkin or
        checkout date is given in query string.
        """

        response = client.get(
            url_for("availabilities")
            + f"?checkin={checkin_date}"
            + "&surface_type=carbonaceous"
        )

        assert response.status_code == 400
