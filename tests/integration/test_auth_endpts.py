from flask import url_for


class TestAuthRegister(object):
    def test_authregister_valid_user(self, client, db):
        """
        AuthRegister endpoint should return 201, access token, and headers
        for valid new user.
        """
        data = dict(
            user_name="some_new_user",
            email="some.new.user@email.com",
            password="somedevpassword",
        )

        response = client.post(url_for("api.auth_register"), json=data)

        assert response.status_code == 201
        assert "access_token" in response.get_json().keys()
        assert "token_type" in response.get_json().keys()
        assert "expires_in" in response.get_json().keys()
