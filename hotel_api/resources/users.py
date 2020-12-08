from datetime import datetime, date

from flask import request, abort
from flask_restx import Namespace, Resource, reqparse, fields, marshal

from hotel_api.models import db, Users

users_ns = Namespace("users")

user = users_ns.model(
    "user",
    {
        "user_name": fields.String(example="clp", required=True),
        "email": fields.String(example="pattersoncharlesl@gmail.com", required=True),
        "is_admin": fields.Boolean(example="True"),
        "is_deactivated": fields.Boolean(example="False"),
        "created_date": fields.DateTime(example="2020-12-01T01:59:39.297904"),
        "last_modified_date": fields.DateTime(example="2020-12-01T01:59:39.297904"),
        "uri": fields.Url("user"),
    },
    strict=True,
)

user_post = users_ns.inherit(
    "user_post", user, {"password": fields.String(required=True)}
)


class UserList(Resource):
    @users_ns.marshal_with(user)
    def get(self):
        """
        Get all users.
        """
        users = Users.query.all()

        return users

    @users_ns.expect(user_post, validate=True)
    @users_ns.response(400, "User with this email or user_name already exists.")
    @users_ns.marshal_with(user, 201)
    def post(self):
        """
        Create new user.
        """
        body = request.get_json()
        user = Users(
            user_name=body["user_name"], email=body["email"], password=body["password"]
        )
        user.add()

        return user, 201


class User(Resource):
    @users_ns.marshal_with(user)
    def get(self, id):
        """
        Get a specified user.
        """
        user = Users.query.get_or_404(id)

        return user

    @users_ns.marshal_with(user)
    @users_ns.expect(user, validate=True)
    def put(self, id):
        """
        Update a specified user.
        """

        user = Users.query.get_or_404(id)
        body = request.get_json()

        # TODO: Why isn't an error being thrown when I pass an undocumented param like password?
        if "password" in body.keys():
            abort(400, "Cannot update password.")

        user.update(body)
        print(user.password)

        return user

    @users_ns.response(200, '{"deactivated": True}')
    def delete(self, id):
        """
        Deactivate specified user.
        """
        user = Users.query.get_or_404(id)
        user.delete()

        return {"deactivated": True}


users_ns.add_resource(UserList, "", endpoint="users")
users_ns.add_resource(User, "/<int:id>", endpoint="user")
