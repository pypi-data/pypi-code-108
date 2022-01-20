import os

from change_event_service.database import db
from sqlalchemy_utils import ScalarListType


class ChangeEventModel(db.Model):
    __tablename__ = os.environ.get('DB_TABLE_NAME')
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    ip = db.Column(db.String)
    user_id = db.Column(db.String)
    new_value = db.Column(db.String)
    object_id = db.Column(db.BigInteger)
    old_value = db.Column(db.String)
    user_name = db.Column(db.String)
    event_time = db.Column(db.TIMESTAMP)
    event_type = db.Column(db.String)
    field_name = db.Column(db.String)
    object_name = db.Column(db.String)
    tag = db.Column(ScalarListType(str))