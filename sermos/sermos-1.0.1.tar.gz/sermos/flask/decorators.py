""" Flask specific decorators (primarily for auth activities and app context)
"""
import os
import logging
from http import HTTPStatus
from functools import wraps
import requests
from rhodb.redis_conf import RedisConnector
from flask import current_app, request
from rho_web.response import abort
from sermos.flask import oidc
from sermos.constants import DEFAULT_AUTH_URL, AUTH_LOCK_KEY, \
    AUTH_LOCK_DURATION, USING_SERMOS_CLOUD

logger = logging.getLogger(__name__)
redis_conn = RedisConnector().get_connection()


def require_login(fn):
    """ Utilize Flask RhoAuth to secure a route with @require_login decorator
    """
    secure_fn = oidc.require_login(fn)

    @wraps(fn)
    def decorated(*args, **kwargs):
        if str(current_app.config['RHOAUTH_ENABLED']).lower() == 'true':
            return secure_fn(*args, **kwargs)
        return fn(*args, **kwargs)

    return decorated


def validate_access_key(access_key: str = None):
    """ Verify whether an Access Key is valid according to Sermos Cloud.

    If deploying in 'local' mode, no validation is done. To deploy in local
    mode, set DEFAULT_BASE_URL=local in your environment.
    """
    # Always 'valid' in local mode
    if not USING_SERMOS_CLOUD:
        return True

    # If get access key from either provided val or environment
    # if None provided.
    access_key = os.environ.get('SERMOS_ACCESS_KEY', access_key)

    # Invalid if None, no need to ask.
    if access_key is None:
        return False

    # Ask cache first
    # TODO update to remove Redis as a dependency, merely an optional feature.
    validated = redis_conn.get(AUTH_LOCK_KEY)
    if validated is not None:
        return True

    # Ask Sermos Cloud (Note: Sermos Cloud's API expects `apikey`)
    headers = {'apikey': access_key}
    r = requests.post(DEFAULT_AUTH_URL, headers=headers, verify=True)

    if r.status_code == 200:
        redis_conn.setex(AUTH_LOCK_KEY, AUTH_LOCK_DURATION, '')
        return True
    return False


def require_accesskey(fn):
    """ Convenience decorator to add to a web route (typically an API)
        when using Flask.

        Usage::
            from sermos import Blueprint, ApiServices
            bp = Blueprint('api_routes', __name__, url_prefix='/api')

            @bp.route('/my-api-route')
            class ApiClass(MethodView):
                @require_access_key
                def post(self, payload: dict):
                    return {}
    """
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        access_key = request.headers.get('accesskey')
        if not access_key:
            access_key = request.args.get('accesskey')

        if validate_access_key(access_key):
            return fn(*args, **kwargs)

        abort(HTTPStatus.UNAUTHORIZED)

    return decorated_view
