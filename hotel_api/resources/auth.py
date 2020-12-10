from datetime import datetime, date

from flask import request
from flask_restx import Namespace, Resource, fields, marshal_with

from hotel_api.models import db, Users
from lib.util_auth import get_token_expire_time

auth_ns = Namespace("auth")

auth_user = auth_ns.model(
    "auth",
    {
        "email": fields.String(required=True, example="some.user@email.com"),
        "user_name": fields.String(requried=True, example="some_user"),
    },
)

auth_password = auth_ns.inherit(
    "auth_password",
    auth_user,
    {
        "password": fields.String(required=True),
    },
)

auth_token = auth_ns.inherit(
    "auth_token",
    auth_user,
    {
        "access_token": fields.String,
        "token_type": fields.String(example="bearer"),
        "expires_in": fields.Integer(example=3600),
    },
)


class AuthRegister(Resource):
    @auth_ns.expect(auth_password, validate=True)
    @marshal_with(auth_token)
    @auth_ns.response(400, "Validation Error")
    @auth_ns.response(
        201,
        "Created",
        auth_token,
        headers={"Cache-Control": "no-store", "Pragma": "no-cache"},
    )
    def post(self):
        """
        Add new user and return JWT token.
        """
        body = request.get_json()
        user = Users(
            user_name=body["user_name"], email=body["email"], password=body["password"]
        )
        user.add()

        access_token = user.encode_access_token()
        expiration = get_token_expire_time()

        response = dict(
            user_name=user.user_name,
            email=user.email,
            access_token=access_token.decode(),
            token_type="bearer",
            expires_in=expiration,
        )
        headers = {"Cache-Control": "no-store", "Pragma": "no-cache"}

        return response, 201, headers


class AuthLogin(Resource):
    @auth_ns.expect(auth_password)
    def post(self):
        """
        Login in user and return JWT token.
        """
        pass


class AuthLogout(Resource):
    def post(self):
        """
        Logout user and blacklist JWT token.
        """
        pass


class AuthUserStatus(Resource):
    @auth_ns.expect(auth_user)
    def get(self):
        """
        Get user's authentication status.
        """
        pass


auth_ns.add_resource(AuthRegister, "/register", endpoint="auth_register")
# auth_ns.add_resource(AuthLogin, "", endpoint="auth_login")
# auth_ns.add_resource(AuthLogout, "", endpoint="auth_logout")
# auth_ns.add_resource(AuthUserStatus, "", endpoint="auth_user_status")