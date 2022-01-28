import logging

from django.db.models import URLField

from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet

logger = logging.getLogger(__name__)


class LinksQuerySet(AuditQuerySet):
    pass


class Model_linksQuerySet(AuditQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)

    def update_or_create(self, defaults=None, **kwargs):
        link = defaults.get('link')

        if link != '' and link is not None:
            link_item = Links.objects.getOptional(link=link)
            if link_item is None:
                try:
                    item = super().get(**kwargs)
                    link_item, _ = Links.objects.update_or_create(id=item.link.id, defaults=dict(link=link))
                except self.model.DoesNotExist:
                    link_item = Links.objects.create(link=link)
            defaults = dict(link=link_item)
            return super().update_or_create(defaults=defaults, **kwargs)
        else:
            return None, None


class LinksManager(AuditManager):

    @classmethod
    def getRecord(cls, record ) :
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return LinksQuerySet(self.model, using=self._db)


class Links(AuditModel):
    link = URLField(db_index=True, unique=True)

    objects = LinksManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Якоря'
