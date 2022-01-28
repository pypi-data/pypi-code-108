"""Copyright (C) 2015-2022 Stack Web Services LLC. All rights reserved."""

from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis

database = SQLAlchemy()
redis = FlaskRedis()
