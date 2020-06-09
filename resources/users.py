from datetime import datetime
from flask import abort
from flask_restful import Resource, reqparse, fields, marshal

# TODO: create a postgres database and store these there
users = [
    {
    'id': 1,
    'username': 'Charlie',
    'password': '12345',
    'created_date': u'2020-05-01T14:09:13.702495',
    'last_updated_date': u'2020-05-01T14:09:13.702495',
    'is_deleted': False
    }
]

user_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'password': fields.String,
    'created_date' : fields.String,
    'last_updated_date' : fields.String,
    'is_deleted': fields.Boolean,
    'uri': fields.Url('user')
}

# Parser for UserList and User resources
reqparse = reqparse.RequestParser() # these lines are for input validation
reqparse.add_argument('username', type = str, required = True,
    help = "No username provided.", location = 'json')
reqparse.add_argument('password', type = str, required = True,
    help = "No password provided.", location = 'json')

class UserList(Resource):
    def __init__(self):
        self.reqparse = reqparse
        super(UserList, self).__init__()

    def get(self):
        """List all users."""
        return { 'users': [marshal(user, user_fields) for user in users] }
    
    def post(self):
        """Add a new reservation to the reservations list."""
        args = self.reqparse.parse_args()
        user = {
                 'id': users[-1]['id'] + 1 if len(users) > 0 else 1,
                 'username': args['username'],
                 'password': args['password'],
                 'created_date': datetime.now().isoformat(),
                 'last_updated_date': datetime.now().isoformat(),
                 'is_deleted': False
                 }    
        users.append(user)
        return {'users': marshal(user, user_fields)}, 201

class User(Resource):
    def __init__(self):
        self.reqparse = reqparse
        super(User, self).__init__()

    def get(self, id):
        """List specified user."""
        user = [user for user in users if user['id'] == id]
        if len(user) == 0:
            abort(404)
        return { 'user': marshal(user[0], user_fields)} 
    
    def put(self, id):
        """Update specified user."""
        user = [user for user in users if user['id'] == id]
        if len(user) == 0:
            abort(404)
        user = user[0]
        args = self.reqparse.parse_args()
        for k,v in args.items():
            if v is not None:
                user[k] = v
        user['last_updated_date'] = datetime.now().isoformat()
        return { 'user': marshal(user, user_fields)}
    
    def delete(self, id):
        """Delete specified user."""
        user = [user for user in users if user['id'] == id]
        if len(user) == 0:
            abort(404)
        user = user[0]
        user['is_deleted'] = True
        user['last_updated_date'] = datetime.now().isoformat()
        return {'deleted': True}
