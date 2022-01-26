import uuid
from enum import Enum

from vatis.asr_commons.config import Language


class Model:
    def __init__(self, uid, language: Language, name: str, description: str = ''):
        assert uid is not None
        assert language is not None
        assert name is not None

        if isinstance(uid, str):
            self.uid = uuid.UUID(uid)
        elif isinstance(uid, uuid.UUID):
            self.uid = uid
        else:
            raise ValueError('Unsupported type: ' + str(type(uid)))

        self.language = language
        self.name = name
        self.description = description

    def __str__(self):
        return f'{str(self.uid)} {self.name} {str(self.language)}'

    def __eq__(self, other):
        if not isinstance(other, Model):
            return NotImplemented

        return self.uid == other.uid

    def __hash__(self):
        return hash(self.uid)


class ModelType(Enum):
    ACOUSTIC: str = 'AM'
    LINGUISTIC: str = 'LM'
