import urllib
from typing import Optional, List
from pydantic import BaseModel
from fastapi import Security, HTTPException, status
from fastapi.security import SecurityScopes
from fastapi_resource_server import JwtDecodeOptions, OidcResourceServer
from typing import Dict, Any
from ..storage import storage

class User(BaseModel):
	username: str
	given_name: Optional[str]
	family_name: Optional[str]
	email: Optional[str]
	scopes: List[str] = []
	profilePicture: Optional[str]


try:
	auth_scheme = OidcResourceServer(
		f"http://{storage['arguments'].auth_server}:8080/auth/realms/{storage['arguments'].auth_realm}",
		scheme_name=storage['arguments'].auth_schema,
		jwt_decode_options=JwtDecodeOptions(verify_aud=False),
	)
except urllib.error.URLError as err:
	auth_scheme = None
	print(f"Warning: Could not initiate auth schema http://{storage['arguments'].auth_server}:8080/auth/realms/{storage['arguments'].auth_realm}: {err}")

def process_user_claim(security_scopes: SecurityScopes, claims: Dict[str, Any] = Security(auth_scheme)) -> User:
	claims.update(username=claims["preferred_username"])
	claims.update(scopes=claims["realm_access"]["roles"])
	claims.update(profilePicture=claims.get('profile', {}).get('picture'))
	user = User.parse_obj(claims)

	if security_scopes.scopes:
		authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
	else:
		authenticate_value = f"Bearer"

	for scope in security_scopes.scopes:
		# Parse wildcard statements a bit more loosely
		if scope.endswith('*'):
			if any([user_scope.startswith(scope[:-1]) for user_scope in user.scopes]) is False:
				raise HTTPException(
					status_code=status.HTTP_401_UNAUTHORIZED,
					detail="Not enough permissions",
					headers={"WWW-Authenticate": authenticate_value},
				)
		# If it's not a wildcard, be strict
		elif scope not in user.scopes:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Not enough permissions",
				headers={"WWW-Authenticate": authenticate_value},
			)

	return user