"""
Various models mixins adding new features/columns to SQLAlchemy models
"""
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
    String,
)
from sqlalchemy.ext.declarative import declared_attr
from .types import (
    ACLType,
    MutableList,
)


class TimeStampedMixin(object):
    @declared_attr
    def created_at(cls):
        return Column(
            DateTime(),
            info={
                'colanderalchemy': {
                    'exclude': True, 'title': "Créé(e) le",
                }
            },
            default=datetime.now,
        )

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime(),
            info={
                'colanderalchemy': {
                    'exclude': True, 'title': "Mis(e) à jour le",
                }
            },
            default=datetime.now,
            onupdate=datetime.now
        )


class OfficialNumberMixin:
    """
    Models that implements that mixin are then able to be numbered using
    numbering sequence mechanisms with guarantees on non-duplicate.

    Models are required to be child of endi.models.node.Node

    Features :

    - templated creation of official_number that may use one or more numeric
      sequences
    - guarantees on official_number (unicity and no gap in sequences)
    - instances with an official_number set should not be deleted

    Inheriting class must:

    - ensure that once official_number is set, instances are not deleted

    Inheriting class may:

    - redefine official_number and company_id as long as name and type are kept
      as-is

    - redefine validation_date_column if the validation is not stored into
      self.date
    """

    validation_date_column = 'date'

    @declared_attr
    def official_number(cls):
        return Column(
            String(255),
            default=None,
        )

    @declared_attr
    def company_id(cls):
        return Column(
            Integer,
            ForeignKey('company.id'),
            nullable=False,
        )

    @property
    def validation_date(self) -> datetime.date:
        return getattr(self, self.validation_date_column)

    @classmethod
    def get_validation_date_column(cls) -> Column:
        # could be turned into @classmethod + @property on Py3.9
        return getattr(cls, cls.validation_date_column)


class PersistentACLMixin(object):
    """Extend pyramid ACL mechanism to offer row-level ACL

    Subclasses may set the following attributes :

    - ``.__default_acl__`` as an ACL or callable returning an ACL, traditionaly
      set at class level.
    - ``.__acl__`` as an ACL or callable returning an ACL, this can be set on
      class or directly on instance.

    If both are defined, ``__acl__``, the more specific, is prefered.

    Use actual callables, not properties, in subclasses to prevent pyramid from
    silently ignoring any AttributeError your callable should trigger.
    """
    @declared_attr
    def _acl(cls):
        """
        Customizable _acl column
        """
        return Column(
            MutableList.as_mutable(ACLType),
            info={
                'colanderalchemy': {'exclude': True},
                'export': {'exclude': True}
            },
        )

    def _get_acl(self):
        # Any AttributeError raised at this function level would be masked.
        # See https://github.com/Pylons/pyramid/pull/2613/files
        if getattr(self, '_acl', None) is None:
            if getattr(self, "__default_acl__", None) is not None:
                return self.__default_acl__
            elif getattr(self, "parent", None) is not None:
                return self.parent.__acl__
            else:
                raise AttributeError('__acl__')
        return self._acl

    def _set_acl(self, value):
        self._acl = value

    def _del_acl(self):
        self._acl = None

    __acl__ = property(_get_acl, _set_acl, _del_acl)


class DuplicableMixin(object):
    """
    Factorize duplication logic on sqlalchemy models

    __duplicable_fields__ attr should contain the list of attributes to be
    copied from a model to its duplicate.
    """
    __duplicable_fields__ = None

    def duplicate(self, factory=None, **kwargs):
        """
        Duplicate all fields listed in __duplicable_fields__ plus optional
        ad-hoc values.

        :param class factory: The new instance class
        :param kwargs: allow to provide ad-hoc values for the attrs of the
          new instance. They will take precedence over copied values.
        :returns: new instance combining fields copied from self, and ad-hoc
          args. The instance is not saved.
        """

        if self.__duplicable_fields__ is None:
            raise NotImplementedError(
               "DuplicableMixin implementors should define "
               + "__duplicable_fields__"
            )

        if factory is None:
            factory = self.__class__

        duplicate_obj = factory()
        for i in self.__duplicable_fields__:
            setattr(duplicate_obj, i, getattr(self, i))
        for k, v in kwargs.items():
            setattr(duplicate_obj, k, v)
        return duplicate_obj
