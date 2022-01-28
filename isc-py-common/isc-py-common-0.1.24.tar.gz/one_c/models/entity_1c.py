import logging

from django.db.models import Model
from transliterate import translit
from transliterate.exceptions import LanguageDetectionError

from isc_common.fields.code_field import CodeField

logger = logging.getLogger(__name__)


class Entity_1c(Model):
    code = CodeField(unique=True)

    @property
    def translited_code(self):
        try:
            return translit(self.code, reversed=True).replace("'", '').replace("'", '')
        except LanguageDetectionError:
            return self.code

    def __str__(self):
        return f"(id: {self.id}, code: {self.code})"

    class Meta:
        verbose_name = 'Сущность 1С'
