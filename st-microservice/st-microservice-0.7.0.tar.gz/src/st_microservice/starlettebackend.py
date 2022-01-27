from typing import Any, Dict, List, Tuple, Optional
from os import getenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.authentication import AuthenticationBackend, AuthenticationError, AuthCredentials, BaseUser
from starlette.responses import Response, JSONResponse
import jwt


# Utilities
def get_required_env(var_name: str) -> str:
    var = getenv(var_name)
    if var is None:
        raise EnvironmentError(f'Could not get {var_name} from ENV')
    return var


def hasenv(var_name: str) -> bool:
    return getenv(var_name, False) is not False


# Database
class DBMiddleware(BaseHTTPMiddleware):
    """ Will start a DB Session at every request and commit or rollback in the end """
    def __init__(self, app, session_class):
        super().__init__(app)
        self.session_class = session_class

    async def dispatch(self, request, call_next) -> Response:
        session = self.session_class()
        request.state.dbsession = session

        # Continue with request
        response = await call_next(request)

        try:  # Try to commit
            session.commit()
            return response
        except SQLAlchemyError:
            session.rollback()
            return JSONResponse({'errors': 'Error while commiting to Database'}, status_code=500)
        finally:
            session.close()


def get_dbsessionclass(database_uri: str, database_args: Optional[dict]):
    """ Helper function to be able to get the Session class outside of the DBMiddleware """
    if database_args is None:
        database_args = {}
    if 'connect_timeout' not in database_args:
        database_args['connect_timeout'] = 5
    engine = create_engine(database_uri, connect_args=database_args)
    return sessionmaker(bind=engine)


# Security
class User(BaseUser):
    def __init__(self, user_id: str, display_name: str, scopes: List[str]):
        self.user_id = user_id
        self._display_name = display_name
        self.scopes = scopes

    @property
    def display_name(self) -> str:
        return self._display_name

    @property
    def is_authenticated(self):
        return True

    @property
    def identity(self) -> str:
        return self.user_id

    def to_json(self) -> Dict[str, Any]:
        return {'user_id': self.user_id, 'display_name': self.display_name, 'scopes': self.scopes}


class JWTAuthBackend(AuthenticationBackend):
    def __init__(self, secret: str):
        self.secret = secret

    @classmethod
    def get_token_from_header(cls, authorization: str) -> str:
        try:
            scheme, token = authorization.split()
        except ValueError:
            raise AuthenticationError('Could not separate Authorization scheme and token')
        if scheme.lower() != 'bearer':
            raise AuthenticationError(f'Authorization scheme {scheme} is not supported')
        return token

    async def authenticate(self, request) -> Optional[Tuple[AuthCredentials, User]]:
        # Try to get token from header then from cookies
        auth_header = request.headers.get('Authorization', None)
        if auth_header is not None:
            token = self.get_token_from_header(auth_header)
        else:
            token = request.cookies.get('token')

        if token is None:
            return None

        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            user = User(payload['user_id'], payload['display_name'], payload['scopes'])
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f'JWT Token error: {e}')
        except Exception as e:
            raise AuthenticationError(f'Authentication error: {e}')

        return AuthCredentials(user.scopes), user


def auth_error_handler(request, exc: Exception):
    response = JSONResponse({'error': str(exc)}, 400)
    response.delete_cookie('token')
    return response


# App factory
def create_app(routes: List[Route], secret: str, root_domain: str, database_uri: str, debug=False, database_ssl=False) -> Starlette:
    authbackend = JWTAuthBackend(secret)

    # Allow origins from both HTTP or HTTPS, root or subdomains, any port
    root_domain_re = r'https?://(.*\.)?{}(:\d*)?'.format(root_domain.replace('.', r'\.'))
    print('Allowed Origins Regex:', root_domain_re)

    database_args = {'sslmode': 'require'} if database_ssl else None

    middleware = [
        Middleware(CORSMiddleware, allow_origin_regex=root_domain_re, allow_credentials=True, allow_methods=['*']),
        Middleware(DBMiddleware, session_class=get_dbsessionclass(database_uri, database_args)),
        Middleware(AuthenticationMiddleware, backend=authbackend, on_error=auth_error_handler)
    ]

    return Starlette(debug=debug, routes=routes, middleware=middleware)
