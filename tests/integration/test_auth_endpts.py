from time import sleep

from flask import url_for

from tests.util import register_user, login_user, get_user, logout_user
from hotel_api.models import BlacklistedTokens


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


class TestAuthLogin(object):
    def test_authlogin_valid_user(self, client, db):
        """
        AuthRegister endpoint should return 201, access token, and headers
        for valid new user.
        """
        data = dict(
            user_name="some_new_user",
            email="some.new.user@email.com",
            password="somedevpassword",
        )

        response = client.post(url_for("api.auth_login"), json=data)

        assert response.status_code == 200
        assert "access_token" in response.get_json().keys()
        assert "token_type" in response.get_json().keys()
        assert "expires_in" in response.get_json().keys()

    def test_authlogin_valid_user_wrong_password(self, client, db):
        """
        AuthRegister endpoint should return 201, access token, and headers
        for valid new user.
        """
        data = dict(
            user_name="some_new_user",
            email="some.new.user@email.com",
            password="wrongpassword",
        )

        response = client.post(url_for("api.auth_login"), json=data)

        assert response.status_code == 401
        assert (
            "Password is incorrect. User authentication failed."
            in response.get_json()["message"]
        )

    def test_authlogin_invalid_user(self, client, db):
        """
        AuthRegister endpoint should return 201, access token, and headers
        for valid new user.
        """
        data = dict(
            user_name="some_fake_user",
            email="some.fake.user@email.com",
            password="fakepassword",
        )

        response = client.post(url_for("api.auth_login"), json=data)

        assert response.status_code == 400
        assert (
            "Given user_name or email is incorrect or user does not exist. Login failed."
            in response.get_json()["message"]
        )


class TestAuthUserStatus(object):
    def test_authuser_status_valid_user(self, client, db):
        """ AuthUserStatus endpoint should return 200 and user data for logged in user.  """
        user = dict(
            user_name="great_user", email="great.user@email.com", password="greatuser"
        )
        register_user(client, **user)
        response = login_user(client, **user)

        assert "access_token" in response.json
        access_token = response.json["access_token"]

        response = get_user(client, access_token)
        assert response.status_code == 200
        assert "email" in response.json and response.json["email"] == user["email"]
        assert "is_admin" in response.json and not response.json["is_admin"]

    def test_authuser_status_valid_user_missing_token(self, client, db):
        """ AuthUserStatus endpoint should return 200 and user data for logged in user.  """
        response = client.get(url_for("api.auth_user_status"))

        assert response.status_code == 401

    def test_authuser_status_valid_user_expired_token(self, client, db):
        """ AuthUserStatus endpoint should return 401 and message for expired token.  """
        user = dict(
            user_name="great_user", email="great.user@email.com", password="greatuser"
        )
        register_user(client, **user)
        response = login_user(client, **user)

        assert "access_token" in response.json
        access_token = response.json["access_token"]

        sleep(6)

        response = get_user(client, access_token)
        assert response.status_code == 401


class TestAuthLogout(object):
    def test_authlogout_valid_user(self, client, db):
        """ AuthLogout endpoint should return 200 and message for user with valid token.  """
        user = dict(
            user_name="great_user", email="great.user@email.com", password="greatuser"
        )
        register_user(client, **user)
        response = login_user(client, **user)

        assert "access_token" in response.json
        access_token = response.json["access_token"]

        response = logout_user(client, access_token, **user)

        assert response.status_code == 200
        blacklist = BlacklistedTokens.query.all()
        assert len(blacklist) == 1
        assert access_token == blacklist[0].token

    def test_authlogout_valid_user_(self, client, db):
        """ AuthLogout endpoint should return 200 and message for user with valid token.  """
        user = dict(
            user_name="great_user", email="great.user@email.com", password="greatuser"
        )
        register_user(client, **user)
        response = login_user(client, **user)

        assert "access_token" in response.json
        access_token = response.json["access_token"]

        response = logout_user(client, access_token, **user)

        assert response.status_code == 200