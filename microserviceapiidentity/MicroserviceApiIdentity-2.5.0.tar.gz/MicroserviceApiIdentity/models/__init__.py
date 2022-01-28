"""Copyright (C) 2015-2022 Stack Web Services LLC. All rights reserved."""

import string
import random
from datetime import datetime
from uuid import uuid4
from hashlib import md5, sha512
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from MicroserviceApiIdentity.db import database


class UsersModel(database.Model):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False)
    email = Column(String(128), unique=True, nullable=False)
    password = Column(String(512))
    is_enabled = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    last_visit_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self, email: str, password: str, is_enabled: int = 0):
        self.email = email
        self.password = password
        self.is_enabled = is_enabled

    def __repr__(self):
        return "<User id=%s email=%s is_enabled=%s created_at=%s updated_at=%s>" % (
            self.id, self.email, self.is_enabled, self.created_at, self.updated_at
        )

    @classmethod
    def auth(cls, email: str, password: str, is_enabled: int = 1) -> bool:
        """User auth method

        >>> UsersModel.auth("email@yandex.ru", "example", 1)
        True

        :return boolean
        """
        is_valid = database.session.query(cls).filter_by(
            email=email,
            password=cls.get_hash(password, ''),
            is_enabled=is_enabled
        ).count()
        return True if is_valid == 1 else False

    @classmethod
    def is_exists_email(cls, email: str) -> bool:
        """Check exists email addres method

        >>> UsersModel.exists_email("email@yandex.ru")
        True

        :return: boolean
        """
        if database.session.query(cls).filter_by(email=email).count() == 0:
            return False
        return True

    @classmethod
    def is_exists_user(cls, user_id: str) -> bool:
        """Check exists user id method

        >>> UsersModel.is_exists_user("9e6cfde2-15f8-4af6-928a-f6e50311b90b")
        True

        :return boolean
        """
        if database.session.query(cls).filter_by(id=user_id).count() == 0:
            return False
        return True

    @classmethod
    def get_item_by_id(cls, user_id: str):
        """Get User details by user ID"""
        return database.session.query(cls).filter_by(id=user_id).first()

    @classmethod
    def get_item_by_email(cls, email):
        """Get User details by user ID"""
        return database.session.query(cls).filter_by(email=email).first()

    @classmethod
    def update_last_visit_time(cls, user_id: str) -> None:
        """Обновление времени последнего визита

        >>> UsersModel.update_last_visit_time("9e6cfde2-15f8-4af6-928a-f6e50311b90b")
        None

        :param user_id: UUID
        :return:
        """
        values = {"last_visit_at": datetime.now()}
        database.session.query(cls).filter(cls.id == user_id).update(values)
        database.session.commit()

    @staticmethod
    def get_hash(password: str, salt: str = '', algorithm: str = 'sha512') -> str:
        """Hash string to md5 string


        >>> UsersModel.hash("example", "", "sha512")
        1a79a4d60de6718e8e5b326e338ae533

        >>> UsersModel.hash("example", "", "md5")
        1a79a4d60de6718e8e5b326e338ae533

        :return str
        """

        if algorithm == 'sha512':
            return sha512('{}{}'.format(
                md5(password.encode()).hexdigest(),
                salt.encode()
            ).encode()).hexdigest()
        # elif algorithm == 'md5':
        else:
            return md5("{}".format(password.encode())).hexdigest()


class AttrsModel(database.Model):
    """Модель атрибутов пользователя"""
    __tablename__ = "attrs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False)
    user = Column(UUID(as_uuid=True), ForeignKey(UsersModel.id), unique=True, nullable=False)
    attr_name = Column(String(32), nullable=False)
    # string, integer, bool
    attr_type = Column(String(32), nullable=False, default="string")
    attr_value = Column(String(128), nullable=True)


class DetailsModel(database.Model):
    __tablename__ = "details"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False)
    user = Column(UUID(as_uuid=True), ForeignKey(UsersModel.id), unique=True, nullable=False)

    fname = Column(String(32), nullable=True)
    lname = Column(String(32), nullable=True)
    address = Column(String(32), nullable=True)
    city = Column(String(32), nullable=True)
    country = Column(String(32), nullable=True)
    state = Column(String(32), nullable=True)
    zipcode = Column(String(32), nullable=True, default=0)

    def __init__(self, user_id: str):
        self.user = user_id

    def __repr__(self):
        return "<Details user={}>".format(self.user)

    @classmethod
    def is_exists_user(cls, user_id: str) -> bool:
        if database.session.query(cls).filter_by(user=user_id).count() == 1:
            return True
        return False

    @classmethod
    def get_item(cls, user):
        return database.session.query(cls).filter_by(user=user).first()


class RecoveryCodesModel(database.Model):
    __tablename__ = "recovery_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False)
    user = Column(UUID(as_uuid=True), ForeignKey(UsersModel.id), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    recovery_code = Column(String, nullable=False)

    def __init__(self, user_id: int, recovery_code: str):
        self.user = user_id
        self.recovery_code = recovery_code

    def __repr__(self):
        return "<RecoveryCode user=%s recovery_code=%s>" % (self.user, self.recovery_code)

    @classmethod
    def check(cls, user: str, code: str) -> bool:
        chk = database.session.query(cls).filter_by(user=user, recovery_code=code).count()
        return True if chk == 1 else False

    @classmethod
    def delete_all_by_user(cls, user: str) -> bool:
        cls.query.filter(cls.user == user).delete()
        database.session.commit()
        return True

    @classmethod
    def delete(cls, user_id: str) -> bool:
        return cls.delete_all_by_user(user_id)

    @staticmethod
    def create(user_id, code):
        """Create record

        :param user_id:
        :param code:
        :return:
        """
        code = RecoveryCodesModel(user_id=user_id, recovery_code=code)
        database.session.add(code)
        database.session.commit()
        return True

    @staticmethod
    def code_generate(size=6, chars=string.ascii_uppercase + string.digits):
        """

        :param size:
        :param chars:
        :return:
        """
        return ''.join(random.choice(chars) for _ in range(size))


class SecretsModel(database.Model):
    """Users Secrets Model"""
    __tablename__ = "secrets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False)
    user = Column(UUID(as_uuid=True), ForeignKey(UsersModel.id), unique=True, nullable=False)

    secret = Column(String(255), unique=False, nullable=False)
    acl = Column(String(255))
    status = Column(Integer, default=0)

    def __init__(self, user_id: str):
        self.user = user_id


class ServicesModel(database.Model):
    __tablename__ = "services"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False)
    name = Column(String(255), unique=False, nullable=False)
    system_name = Column(String(255), unique=False, nullable=False)
    url_public = Column(String(255), nullable=False)
    url_internal = Column(String(255), nullable=False)
    url_service = Column(String(255), nullable=False)
    # 0 - inactive, 1 - active
    is_active = Column(Integer, default=0)
    status = Column(Integer, default=0)
