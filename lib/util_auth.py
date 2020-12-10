from flask import current_app


def get_token_expire_time():
    """ Return token expiration time in seconds.  """
    token_age_h = current_app.config.get("TOKEN_EXPIRE_HOURS")
    token_age_m = current_app.config.get("TOKEN_EXPIRE_MINUTES")
    expires_in_seconds = token_age_h * 3600 + token_age_m * 60

    return expires_in_seconds if not current_app.config["TESTING"] else 5