"""Configuration for the CIDC API."""
from .db import get_sqlalchemy_database_uri  # for CFns
from .secrets import get_secrets_manager  # for CFns
