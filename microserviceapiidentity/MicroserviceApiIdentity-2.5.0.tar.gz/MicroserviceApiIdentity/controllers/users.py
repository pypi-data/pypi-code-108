"""Copyright (C) 2015-2022 Stack Web Services LLC. All rights reserved."""
import string
import random
from MicroserviceApiIdentity.db import database
from MicroserviceApiIdentity.models import UsersModel, RecoveryCodesModel


class UsersController:
    def __init__(self, user_id=None):
        if user_id:
            self.user_id = user_id

    @staticmethod
    def user_id_by_email(email):
        return database.session.query(UsersModel.id).filter_by(email=email).scalar()

    @staticmethod
    def user_exists_by_email(self, email):
        if UsersModel.query().filter(UsersModel.email == email).count() == 0:
            return False
        return True

    # TODO: remove
    def user_get(self):
        return UsersModel.select().where(UsersModel.id == self.user_id).limit(1)[0]

    def get(self):
        return UsersModel.select().where(UsersModel.id == self.user_id).limit(1)[0]

    def update(self, user_id, **kwargs):
        pwd_hash = UsersModel.get_hash(kwargs['password'])
        if 'password' in kwargs:
            database.session.query(UsersModel).filter(UsersModel.id == user_id).update({"password": pwd_hash})
            database.session.commit()
        return True

    def generate_password(self, size=14, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))
