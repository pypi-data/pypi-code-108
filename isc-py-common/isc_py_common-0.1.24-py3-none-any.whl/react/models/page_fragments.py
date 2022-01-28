import logging

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from react.models.fragments import Fragments
from react.models.pages import Pages

logger = logging.getLogger(__name__)


class Page_fragmentsQuerySet(AuditQuerySet):
    pass


class Page_fragmentsManager(AuditManager):

    @classmethod
    def getRecord(cls, record ) :
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Page_fragmentsQuerySet(self.model, using=self._db)


class Page_fragments(AuditModel):
    fragment = ForeignKeyProtect(Fragments)
    page = ForeignKeyProtect(Pages)

    objects = Page_fragmentsManager()

    def __str__(self):
        return f'ID:{self.id}, fragment: [{self.fragment}], page: [{self.page}]'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс таблица'
        unique_together = (('page', 'fragment'),)
