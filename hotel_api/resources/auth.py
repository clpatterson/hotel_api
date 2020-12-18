from datetime import datetime, date

from flask import request, abort
from flask_restx import Namespace, Resource, fields, marshal_with

from hotel_api.models import db, Users, BlacklistedTokens
from lib.util_auth import (
    get_token_expire_time,
    create_auth_success_response,
    token_required,
)

auth_ns = Namespace("auth")

auth_user = auth_ns.model(
    "auth_user",
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

auth_status = auth_ns.inherit(
    "auth_status",
    auth_user,
    {
        "token_expires_in": fields.Integer(example=3600),
        "is_admin": fields.Boolean(example="False"),
        "is_deactivated": fields.Boolean(example="False"),
        "created_date": fields.DateTime(example="2020-12-01T01:59:39.297904"),
        "last_modified_date": fields.DateTime(example="2020-12-01T01:59:39.297904"),
        "uri": fields.Url("api.user"),
    },
)


class AuthRegister(Resource):
    @auth_ns.expect(auth_password, validate=True)
    @marshal_with(auth_token)
    @auth_ns.response(400, "Validation error.")
    @auth_ns.response(
        201,
        "Created.",
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

        response, headers = create_auth_success_response(
            user_name=user.user_name, email=user.email, access_token=access_token
        )

        return response, 201, headers


class AuthLogin(Resource):
    @auth_ns.expect(auth_password, validate=True)
    @marshal_with(auth_token)
    @auth_ns.response(400, "Validation error.")
    @auth_ns.response(401, "Unauthorized.")
    @auth_ns.response(
        200,
        "Success.",
        auth_token,
        headers={"Cache-Control": "no-store", "Pragma": "no-cache"},
    )
    def post(self):
        """
        Login in user and return JWT token.
        """
        body = request.get_json()
        user = Users.query.filter(
            Users.user_name == body["user_name"], Users.email == body["email"]
        ).first()

        if not user:
            abort(
                400,
                "Given user_name or email is incorrect or user does not exist. Login failed.",
            )
        if not user.check_password(body["password"]):
            abort(401, "Password is incorrect. User authentication failed.")

        access_token = user.encode_access_token()

        response, headers = create_auth_success_response(
            user_name=user.user_name, email=user.email, access_token=access_token
        )

        return response, 200, headers


class AuthLogout(Resource):
    @auth_ns.doc(security="Bearer")
    @auth_ns.response(200, "Successfully logged out.")
    @auth_ns.response(400, "Validation error.")
    @auth_ns.response(401, "Token is invalid or expired.")
    @token_required
    def post(self):
        """
        Logout user and blacklist JWT token.
        """
        access_token = self.post.token
        expires_at = self.post.expires_at

        blacklisted_token = BlacklistedTokens(access_token, expires_at)
        blacklisted_token.add()

        return "Successfully logged out.", 200


class AuthUserStatus(Resource):
    @auth_ns.doc(security="Bearer")
    @auth_ns.response(200, "Token is currently valid.", auth_status)
    @auth_ns.response(400, "Validation error.")
    @auth_ns.response(401, "Token is invalid or expired.")
    @marshal_with(auth_status)
    @token_required
    def get(self):
        """
        Get user's authentication status.
        """
        user_id = self.get.__wrapped__.id
        user = Users.query.filter(Users.id == user_id).first()

        expires_at = self.get.__wrapped__.expires_at
        token_expires_in = (
            datetime.fromtimestamp(expires_at) - datetime.now()
        ).total_seconds()

        response = dict(
            user.__dict__, expires_at=expires_at, token_expires_in=token_expires_in
        )

        return response


auth_ns.add_resource(AuthRegister, "/register", endpoint="auth_register")
auth_ns.add_resource(AuthLogin, "/login", endpoint="auth_login")
auth_ns.add_resource(AuthLogout, "/logout", endpoint="auth_logout")
auth_ns.add_resource(AuthUserStatus, "/status", endpoint="auth_user_status")