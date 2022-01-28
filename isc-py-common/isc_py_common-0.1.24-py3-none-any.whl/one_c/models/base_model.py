import logging

from django.db.models import Model

from isc_common.models.base_ref import BaseRefQuerySet, BaseRefManager

logger = logging.getLogger(__name__)


class BaseQuerySet(BaseRefQuerySet):
    pass


class BaseManager(BaseRefManager):
    def get_queryset(self):
        return BaseQuerySet(model=self.model)


class Base_model(Model):
    description = None
    parent = None
    get_parent = None

    def get_parent_name(self, parent, description):
        if not self.description:
            self.description = ''

        if not parent:
            return description

        item = parent
        description = f'/{item.description}{description}'
        if item.parent:
            return self.get_parent_name(self.get_parent(parent=item.parent), description)
        return description

    @property
    def full_name(self):

        if not self.description:
            self.description = ''

        description = f'/{self.description}'
        return self.get_parent_name(self.get_parent(parent=self.parent), description)

    def __str__(self):
        return f"{self.id}"

    objects = BaseManager()

    class Meta:
        verbose_name = 'Базовый класс для всех объектов 1С'
        abstract = True
