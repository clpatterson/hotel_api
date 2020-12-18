from flask import url_for

USER_NAME = "test_user"
EMAIL = "test_user@email.com"
PASSWORD = "test1234"


def register_user(client, user_name, email, password):
    data = dict(user_name=user_name, email=email, password=password)
    return client.post(url_for("api.auth_register"), json=data)


def login_user(client, user_name, email, password):
    data = dict(user_name=user_name, email=email, password=password)
    return client.post(url_for("api.auth_login"), json=data)


def get_user(client, access_token):
    return client.get(
        url_for("api.auth_user_status"),
        headers={"Authorization": f"Bearer {access_token}"},
    )


def logout_user(client, access_token, user_name, email, password):
    data = dict(user_name=user_name, email=email, password=password)
    return client.post(
        url_for("api.auth_logout"),
        json=data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
