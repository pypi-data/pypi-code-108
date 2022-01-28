import logging

from django.db import transaction
from django.db.models import BigIntegerField

from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.models.base_ref import BaseRefManager, BaseRefQuerySet, BaseRef
from isc_common.models.tree_audit import TreeAuditModelManager
from react.models.fragments_item_types import Fragments_item_types
from react.models.page_fragments import Page_fragments
from react.models.pages import Pages

logger = logging.getLogger(__name__)


class Fragments_4_page_viewQuerySet(BaseRefQuerySet):
    pass


class Fragments_4_page_viewManager(BaseRefManager):
    def deleteFromRequest(self, request, removed=None, ):
        request = DSRequest(request=request)
        res = 0
        tuple_ids = request.get_olds_tuple_ids('page_fragment_id')
        with transaction.atomic():
            for id, mode in tuple_ids:
                if mode == 'hide':
                    Page_fragments.objects.filter(id=id).soft_delete()
                    res += 1
                elif mode == 'visible':
                    Page_fragments.objects.filter(id=id).soft_restore()
                else:
                    qty, _ = Page_fragments.objects.filter(id=id).delete()
                    res += qty
        return res

    @classmethod
    def getRecord(cls, record ) :
        res = {
            'code': record.code,
            'deliting': record.deliting,
            'description': record.description,
            'editing': record.editing,
            'id': record.id,
            'name': record.name,
            'page_fragment_id': record.page_fragment_id,
            'parent_id': record.parent_id,
            'type__name': record.type.name,
            'type_id': record.type.id,
        }
        return res

    def get_queryset(self):
        return Fragments_4_page_viewQuerySet(self.model, using=self._db)


class Fragments_4_page_view(BaseRef):
    parent_id = BigIntegerField(db_index=True, null=True, blank=True)
    page = ForeignKeyProtect(Pages)
    type = ForeignKeyProtect(Fragments_item_types)
    page_fragment_id = BigIntegerField()

    objects = Fragments_4_page_viewManager()
    tree_objects = TreeAuditModelManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Структура фрагмента'
        db_table = 'react_fragments_4_page_view'
        managed = False
