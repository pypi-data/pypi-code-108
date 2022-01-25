import os

from univer_db.config import Config
from univer_db.orm import get_session


config = Config(
    host=os.environ.get('UNIVER_HOST'),
    user=os.environ.get('UNIVER_USER'),
    password=os.environ.get('UNIVER_PASSWORD')
)

Session = get_session(config)
