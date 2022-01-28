import logging

from django.db.models import Model, PositiveIntegerField
from transliterate import translit
from transliterate.exceptions import LanguageDetectionError

from isc_common.fields.code_field import CodeField
from isc_common.fields.related import ForeignKeyProtect
from one_c.models.entity_1c import Entity_1c

logger = logging.getLogger(__name__)


class One_c_params_entity_view(Model):
    code = CodeField(verbose_name='Код параметтра')
    entity = ForeignKeyProtect(Entity_1c, verbose_name='Сущность 1С')

    @property
    def translited_code(self):
        try:
            return translit(self.code, reversed=True).replace("'", '').replace("'", '')
        except LanguageDetectionError:
            return self.code

    def __str__(self):
        return f"{self.id}"

    class Meta:
        managed = False
        db_table = 'one_c_params_entity_view'
        verbose_name = 'Все параметры 1С документов'
