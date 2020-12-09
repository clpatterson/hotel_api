import time

import werkzeug

from hotel_api.models import Users


class TestUsersModel(object):
    def test_encode_access_token(self, db, user):
        access_token = user.encode_access_token()
        assert isinstance(access_token, bytes)

    def test_decode_access_token(self, user):
        access_token = user.encode_access_token()
        user_dict = Users.decode_access_token(access_token)
        print("user_dict")

        assert isinstance(user_dict, dict)
        assert user.id == user_dict["id"]
        assert user.is_admin == user_dict["admin"]

    def test_decode_access_token_expired(self, user):
        access_token = user.encode_access_token()
        time.sleep(6)

        try:
            Users.decode_access_token(access_token)
        except werkzeug.exceptions.Unauthorized as e:
            code = e.code
            message = e.description

        assert code == 401
        assert message == "Access token expired. Please log in again."
