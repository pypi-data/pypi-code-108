import logging

from bitfield import BitField
from crypto.models.crypto_file import Crypto_file
from django.db.models import DateTimeField

logger = logging.getLogger(__name__)


class Files_1c(Crypto_file):
    file_modification_time = DateTimeField(verbose_name='Дата время поcледнего модификации документа')
    props = BitField(flags=(('imp', 'Импорт'), ('exp', 'Экспорт')), db_index=True)

    def __str__(self):
        return f"id: {self.id}, real_name: {self.real_name}"

    class Meta:
        verbose_name = 'Файлы 1С'
