from transliterate import translit
from transliterate.exceptions import LanguageDetectionError

from isc_common import setAttr


class EntityProperties:
    code = None

    def used_field(self):
        return []

    def __init__(self):
        from one_c.models.entity_1c import Entity_1c
        if self.code:
            self.id = Entity_1c.objects.get(code=self.code).id


class ForeignKey:
    def __init__(self, **kwargs):
        self.type = kwargs.get('type')
        self.to = kwargs.get('to', "'self'")
        self.pk = kwargs.get('pk', "id")

    def __str__(self):
        return f'{self.type}({self.to})'


class ForeignKeyProtect(ForeignKey):
    def __init__(self, **kwargs):
        setAttr(kwargs, 'type', 'ForeignKeyProtect')
        super().__init__(**kwargs)


class Field:
    foreign_key = None

    @classmethod
    def string(cls):
        return "string"

    @classmethod
    def float(cls):
        return "float"

    @classmethod
    def int(cls):
        return "int"

    @classmethod
    def uuid(cls):
        return "uuid"

    @classmethod
    def boolean(cls):
        return "boolean"

    @property
    def translited_name(self):
        try:
            return translit(self.name, reversed=True).replace("'", '').replace("'", '')
        except LanguageDetectionError:
            return self.name

    @property
    def translited_record_path(self):
        if self.foreign_key:
            path = f'{self.name}.{self.foreign_key.pk}'
        else:
            path = self.name
        try:
            return translit(path, reversed=True).replace("'", '').replace("'", '')
        except LanguageDetectionError:
            return path

    @property
    def translited_alias(self):
        try:
            return translit(self.alias, reversed=True).replace("'", '').replace("'", '')
        except LanguageDetectionError:
            return self.alias

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.alias = kwargs.get('alias', self.name)
        self.title = kwargs.get('title', self.name)
        self.type = kwargs.get('type', Field.string())
        self.primary_key = kwargs.get('primary_key', False)
        self.required = kwargs.get('required', False)
        self.length = kwargs.get('length', 255),
        self.hidden = kwargs.get('hidden', False)
        self.canEdit = kwargs.get('canEdit', True)
        self.canFilter = kwargs.get('canFilter', True)
        self.align = kwargs.get('align', '"left"')
        self.canSort = kwargs.get('canSort', False)
        self.format = kwargs.get('format', 'undefined')
        self.canGroupBy = kwargs.get('canGroupBy', False)
        self.index = kwargs.get('index', 0)
        self.mask = kwargs.get('mask', '""')
        self.lookup = kwargs.get('lookup', False)
        self.only_datasource = kwargs.get('only_datasource', False)
        if kwargs.get('foreign_key'):
            if isinstance(kwargs.get('foreign_key'), ForeignKey):
                self.foreign_key = kwargs.get('foreign_key')
            else:
                raise Exception(f"{kwargs.get('foreign_key')} must be a ForeignKey instance")


class Entities:

    def __init__(self, entities=[]):
        self.entities = entities

    def get_field(self, id, name):
        _entity = [_entity for _entity in self.entities if _entity.id == id]
        if len(_entity) == 0:
            return None
        else:
            fields = [field for field in _entity[0].used_field() if field.name == name]
            if len(fields) == 0:
                return None
            else:
                return fields[0]

    def get_fields(self, id):
        _entity = [_entity for _entity in self.entities if _entity.id == id]
        if len(_entity) == 0:
            return None
        else:
            return [field for field in _entity[0].used_field()]
