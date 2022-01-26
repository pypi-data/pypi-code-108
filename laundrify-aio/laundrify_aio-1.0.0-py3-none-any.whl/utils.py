import re

def validate_auth_code(code: str):
	return bool( re.match(r"^\d{3}-\d{3}$", code) )