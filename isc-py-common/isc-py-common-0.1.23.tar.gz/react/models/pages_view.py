import logging

from django.db.models import BooleanField

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.base_ref import BaseRefManager, BaseRefQuerySet, BaseRefHierarcy
from react.models.page_level_types import Page_level_types
from react.models.pages import PagesManager

logger = logging.getLogger(__name__)


class Pages_viewQuerySet(BaseRefQuerySet):
    pass


class Pages_viewManager(BaseRefManager):

    @classmethod
    def getRecord(cls, record ) :
        res = {
            'application': record.application,
            'code': record.code,
            'deliting': record.deliting,
            'description': record.description,
            'editing': record.editing,
            'id': record.id,
            'name': record.name,
            'parent_id': record.parent.id if record.parent else None,
            'props': record.props,
            'type__name': record.type.name,
            'type_id': record.type.id,
        }
        return res

    def get_queryset(self):
        return Pages_viewQuerySet(self.model, using=self._db)


class Pages_view(BaseRefHierarcy):
    application = BooleanField()
    props = PagesManager.props()
    type = ForeignKeyProtect(Page_level_types)

    objects = Pages_viewManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Структура страницы'
        db_table = 'react_pages_view'
        managed = False
