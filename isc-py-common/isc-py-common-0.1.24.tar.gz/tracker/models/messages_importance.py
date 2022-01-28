import logging

from isc_common.models.base_ref import BaseRef, BaseRefManager, BaseRefQuerySet

logger = logging.getLogger(__name__)


class Messages_importanceQuerySet(BaseRefQuerySet):
    pass


class Messages_importanceManager(BaseRefManager):

    @classmethod
    def getRecord(cls, record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'description': record.description,
        }
        return res

    def get_queryset(self):
        return Messages_importanceQuerySet(self.model, using = self._db)


class Messages_importance(BaseRef):
    objects = Messages_importanceManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Важность дел'
