import logging
import operator

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from django.db.models.constants import LOOKUP_SEP

logger = logging.getLogger(__name__)


class PropertyField:
    def __init__(self, method):
        self.name = method
        self.verbose_name = method.fget.short_description
        self.internal_type = method.fget.internal_type

    def get_internal_type(self):
        return self.internal_type


class ResolverValidationError(Exception):
    def __init__(self, errors):
        super().__init__("Validation errors")
        self.errors = errors


class MetaResolver:
    def __init__(self, model):
        self.model = model

    def get_field(self, lookup):
        path = lookup.split(LOOKUP_SEP)
        path, field_name = path[:-1], path[-1]
        model = self.model
        for e in path:
            model = model._meta.get_field(e).related_model
        attr = getattr(model, field_name)
        if isinstance(attr, property):
            return PropertyField(attr)
        return model._meta.get_field(field_name)


class ObjectResolver:
    def __init__(self, object):
        self.object = object
        self.related_objects = []
        self.lookups = {}

    def get_value(self, lookup):
        try:
            return operator.attrgetter(
                lookup.replace(LOOKUP_SEP, '.'))(self.object)
        except ObjectDoesNotExist:
            return

    def set_value(self, lookup, value):
        path = lookup.split(LOOKUP_SEP)
        path, fname = '__'.join(path[:-1]), path[-1]
        if path:
            fobj = self.get_value(path)
            self.related_objects.append(fobj)
        else:
            fobj = self.object
        self.lookups[fname] = lookup
        attr = getattr(type(fobj), fname)
        if isinstance(attr, property) and attr.fset is None:
            # Ignore property if there is no explicit setter.
            return
        setattr(fobj, fname, value)

    def set_values(self, **values):
        for attr, val in values.items():
            self.set_value(attr, val)

    def validate(self, **kwargs):
        errors = {}
        for obj in [*self.related_objects, self.object]:
            try:
                obj.full_clean(**kwargs)
            except ValidationError as e:
                errors.update({
                    self.lookups.get(k, k): v
                    for k, v in e.message_dict.items()})
        if errors:
            raise ResolverValidationError(errors)

    def save(self):
        if self.related_objects:
            with transaction.atomic():
                for obj in [*self.related_objects, self.object]:
                    obj.save()
        else:
            self.object.save()
