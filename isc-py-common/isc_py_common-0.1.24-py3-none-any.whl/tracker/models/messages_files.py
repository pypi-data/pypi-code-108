import logging

from crypto.models.crypto_file import Crypto_file, CryptoManager, CryptoQuerySet

logger = logging.getLogger(__name__)


class Messages_filesQuerySet(CryptoQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Messages_filesManager(CryptoManager):

    @classmethod
    def getRecord(cls, record):
        res = {
            'id': record.id,
            'format': record.format,
            'mime_type': record.mime_type,
            'size': record.size if not str(record.size).startswith('.') else str(record.size).replace('.', '0.'),
            'real_name': record.real_name,
        }
        return res

    def get_queryset(self):
        return Messages_filesQuerySet(self.model, using = self._db)


class Messages_files(Crypto_file):
    objects = Messages_filesManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Файлы'
