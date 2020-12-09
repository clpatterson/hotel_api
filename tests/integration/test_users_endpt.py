from flask import url_for


class TestUserList(object):
    def test_userlist_get_users(self, client, db):
        """
        Users endpoint should return 200 and user data without password
         for valid get request.
        """
        response = client.get(url_for("users"))

        assert response.status_code == 200
        assert "password" not in response.get_json()[0].keys()
        assert "user_name" in response.get_json()[0].keys()

    def test_userlist_post_new_valid_user(self, client, db):
        """
        Users endpoint should return 201 and user data (excluding password)
         for valid new user.
        """
        data = {
            "user_name": "another_test_user",
            "email": "another.test.user@email.com",
            "password": "testpassword",
        }
        response = client.post(url_for("users"), json=data)

        assert response.status_code == 201
        assert "password" not in response.get_json().keys()
        assert "user_name" in response.get_json().keys()

    def test_userlist_post_duplicate_user(self, client, db):
        """
        Users endpoint should return 400 and user already exists error message
        for duplicate user.
        """
        data = {
            "user_name": "another_test_user",
            "email": "another.test.user@email.com",
            "password": "testpassword",
        }
        response = client.post(url_for("users"), json=data)

        assert response.status_code == 400
        assert "User with this email already exists." in response.get_json()["message"]

    def test_userlist_post_new_user_missing_email(self, client, db):
        """
        Users endpoint should return 400 and error message for new user missing email.
        """
        data = {
            "user_name": "another_test_user",
            "password": "testpassword",
        }
        response = client.post(url_for("users"), json=data)

        assert response.status_code == 400
        assert "email" in response.get_json()["errors"].keys()

    def test_userlist_post_new_user_missing_password(self, client, db):
        """
        Users endpoint should return 400 and missing password error for
        new user missing password.
        """
        data = {
            "user_name": "another_test_user",
            "email": "another.test.user@email.com",
        }
        response = client.post(url_for("users"), json=data)

        assert response.status_code == 400
        assert "password" in response.get_json()["errors"].keys()


class TestUser(object):
    def test_get_valid_user(self, client, db):
        """User endpoint should return 200 and user data (excluding password) """
        response = client.get(url_for("user", id=1))

        assert response.status_code == 200
        assert "password" not in response.get_json().keys()
        assert "roger_briggs" in response.get_json()["user_name"]

    def test_get_user_invalid_user_id(self, client, db):
        """User endpoint should return 404 and not found message for invalid user id. """
        response = client.get(url_for("user", id=3000))

        assert response.status_code == 404

    def test_update_user_valid_params(self, client, db):
        """ User endpoint should return 200 and updated user data after valid update. """
        data = {"user_name": "roger_briggs", "email": "roger.briggs@new_email.com"}

        response = client.put(url_for("user", id=1), json=data)

        assert response.status_code == 200
        assert response.get_json()["email"] == "roger.briggs@new_email.com"

    def test_update_user_missing_user_name_param(self, client, db):
        """ User endpoint should return 400 when required params are missing. """
        data = {"email": "roger.briggs@new_email.com"}

        response = client.put(url_for("user", id=1), json=data)

        assert response.status_code == 400

    # TODO: Resolve issue with strict param in model
    def test_update_user_invalid_password_param(self, client, db):
        """ User endpoint should return 400 when user attemps to pass password param to update. """
        data = {
            "user_name": "roger_briggs",
            "email": "roger.briggs@new_email.com",
            "password": "newpassword",
        }

        response = client.put(url_for("user", id=1), json=data)
        print("resp", response.get_json())

        assert response.status_code == 400

    def test_update_user_email_to_existing_email(self, client, db):
        """
        User endpoint should return 400 and error message
        when email is already in use.
        """
        data = {"user_name": "roger_briggs", "email": "oprah.winfrey@email.com"}

        response = client.put(url_for("user", id=1), json=data)

        assert response.status_code == 400
        assert (
            response.get_json()["message"]
            == "User with this email already exists. Update failed."
        )

    def test_update_user_name_to_existing_user_name(self, client, db):
        """
        User endpoint should return 200 and error message when
        user_name is already in use.
        """
        data = {"user_name": "oprah_winfrey", "email": "roger.briggs@new_email.com"}

        response = client.put(url_for("user", id=1), json=data)

        assert response.status_code == 400
        assert (
            response.get_json()["message"]
            == "User with this user_name already exists. Update failed."
        )

    # TODO: Add tests to confirm all users outstanding reservations are cancelled
    #  when they're account is deactivated.
    def test_delete_valid_user(self, client, db):
        """User endpoint should return 200 and user data (excluding password) """
        response = client.delete(url_for("user", id=1))

        assert response.status_code == 200
        assert "deactivated" in response.get_json().keys()

    def test_delete_invalid_user_id(self, client, db):
        """User endpoint should return 404 and not found message for invalid user id. """
        response = client.delete(url_for("user", id=3000))

        assert response.status_code == 404