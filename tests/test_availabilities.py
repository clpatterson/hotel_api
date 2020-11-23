from flask import url_for


class TestAvailabilities(object):
    def test_availabilities_for_valid_input(self, client):
        """
        Availabilities endpoint should return 200 status code and
        json response.
        """
        response = client.get(
            url_for("availabilities") + "?checkin=2020-10-01" + "&checkout=2020-10-04"
        )
        json_response = response.get_json()

        assert response.status_code == 200
        assert "name" in json_response["hotels"][0]

    def test_availabilities_for_multiple_surface_types(self, client):
        """
        Availabilities endpoint should return 200 for multiple
        surface types in query string.
        """
        response = client.get(
            url_for("availabilities")
            + "?checkin=2020-10-01"
            + "&checkout=2020-10-04"
            + "&surface_type=silicaceous"
            + "&surface_type=carbonaceous"
        )

        assert response.status_code == 200

    def test_availabilities_for_multiple_hotel_names(self, client):
        """
        Availabilities endpoint should return 200 for multiple hotel names
        in query string.
        """

        response = client.get(
            url_for("availabilities")
            + "?checkin=2020-10-01"
            + "&checkout=2020-10-04"
            + "&name=1_Ceres"
            + "&name=8_Flora"
        )

        assert response.status_code == 200

    def test_availabilities_for_multiple_room_types(self, client):
        """
        Availabilities endpoint should return 200 for multiple room types
        in query string.
        """

        response = client.get(
            url_for("availabilities")
            + "?checkin=2020-10-01"
            + "&checkout=2020-10-04"
            + "&room_type=king"
            + "&room_type=double"
        )

        assert response.status_code == 200

    def test_availabilities_for_invalid_room_type(self, client):
        """
        Availabilities endpoint should return 400 for invalid room_type
        in query string.
        """

        response = client.get(
            url_for("availabilities")
            + "?checkin=2020-10-01"
            + "&checkout=2020-10-04"
            + "&room_type=king"
            + "&room_type=cool_room"
        )

        assert response.status_code == 400

    def test_availabilities_for_invalid_surface_type(self, client):
        """
        Availabilities endpoint should return 400 for invalid
        surface types in query string.
        """

        response = client.get(
            url_for("availabilities")
            + "?checkin=2020-10-01"
            + "&checkout=2020-10-04"
            + "&surface_type=dirty"
            + "&surface_type=carbonaceous"
        )

        assert response.status_code == 400

    def test_availabilities_for_missing_dates(self, client):
        """
        Availabilities endpoint should return 400 when no checkin or
        checkout date is given in query string.
        """

        response = client.get(
            url_for("availabilities")
            + "?checkin=2020-10-01"
            + "&surface_type=carbonaceous"
        )

        assert response.status_code == 400
