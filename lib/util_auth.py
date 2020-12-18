from functools import wraps

from flask import current_app, request

from hotel_api.models import Users
from hotel_api.exceptions import ApiUnauthorized, ApiForbidden


def get_token_expire_time():
    """ Return token expiration time in seconds.  """
    token_age_h = current_app.config.get("TOKEN_EXPIRE_HOURS")
    token_age_m = current_app.config.get("TOKEN_EXPIRE_MINUTES")
    expires_in_seconds = token_age_h * 3600 + token_age_m * 60

    return expires_in_seconds if not current_app.config["TESTING"] else 5


def create_auth_success_response(user_name, email, access_token):
    """ Return response and headers for successful authorization. """
    response = dict(
        user_name=user_name,
        email=email,
        access_token=access_token.decode(),
        token_type="bearer",
        expires_in=get_token_expire_time(),
    )
    headers = {"Cache-Control": "no-store", "Pragma": "no-cache"}

    return response, headers


def token_required(f):
    """Execute function if request contains valid access token."""

    @wraps(f)
    def decorated(*args, **kwargs):
        print(decorated)
        token_payload = _check_access_token(admin_only=False)
        for name, val in token_payload.items():
            setattr(decorated, name, val)
        print(dir(decorated))
        return f(*args, **kwargs)

    return decorated


def admin_token_required(f):
    """Execute function if request contains valid access token AND user is admin."""

    @wraps(f)
    def decorated(*args, **kwargs):
        token_payload = _check_access_token(admin_only=True)
        if not token_payload["admin"]:
            raise ApiForbidden()
        for name, val in token_payload.items():
            setattr(decorated, name, val)
        return f(*args, **kwargs)

    return decorated


def _check_access_token(admin_only):
    token = request.headers.get("Authorization")
    if not token:
        raise ApiUnauthorized(description="Unauthorized", admin_only=admin_only)
    result = Users.decode_access_token(token)
    if result["status"] == "Failed":
        raise ApiUnauthorized(
            description=result["message"],
            admin_only=admin_only,
            error="invalid_token",
            error_description=result["message"],
        )
    return result