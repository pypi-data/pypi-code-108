import logging

from bitfield import BitField
from django.db import connection
from django.db.models import TextField
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet

logger = logging.getLogger(__name__)


class Model_text_informationsQuerySet(AuditQuerySet):

    def update_or_create(self, defaults=None, **kwargs):
        text = defaults.get('text')

        if text != '' and text is not None:
            try:
                item = super().get(**kwargs)
                text_item, _ = Text_informations.objects.update_or_create(id=item.id, defaults=dict(text=text))
            except self.model.DoesNotExist:
                text_informations = list(Text_informations.objects.filter(text=text))
                if len(text_informations) > 0:
                    text_item = text_informations[0]
                else:
                    text_item = Text_informations.objects.create(text=text)

            defaults = dict(text=text_item)
            return super().update_or_create(defaults=defaults, **kwargs)


class Text_informationsQuerySet(AuditQuerySet):
    pass


class Text_informationsManager(AuditManager):
    @classmethod
    def props(cls):
        return BitField(flags=(
            ('checked_src_icluded', 'Выполнена проверка на содержащие картинки'),  # 1
        ), default=0, db_index=True)

    @classmethod
    def get_text( cls , model_id , model_code , model , model_text , model_text_fk ) :
        with connection.cursor() as cursor :
            cursor.execute( f'''select cml.id, cml.text
                                from {model} as lg
                                join {model_text} as lgl on lg.id = lgl.{model_text_fk}
                                join isc_common_text_informations as cml on lgl.text_id = cml.id
                                where lg.id = %s
                                and lgl.code = %s''' , [ model_id , model_code ] )
            row = cursor.fetchone()
            if row is None :
                return None , None
            else :
                id , text = row
            return id , text

    @classmethod
    def getRecord(cls, record ) :
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
            'text': record.text,
        }
        return res

    def get_queryset(self):
        return Text_informationsQuerySet(self.model, using=self._db)


class Text_informations(AuditModel):
    props = Text_informationsManager.props()
    text = TextField()

    objects = Text_informationsManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Якоря'
