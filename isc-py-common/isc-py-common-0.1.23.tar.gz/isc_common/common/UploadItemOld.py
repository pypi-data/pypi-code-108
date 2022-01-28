import json
import logging
import os
import shutil
import zipfile

from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from django.conf import settings


class UploadItem:
    id = None
    file_format = None
    file_mime_type = None
    file_size = None
    real_file_name = None
    stored_file_name = None

    code = None
    description = None
    date = None
    date_sign = None
    vatdescr = None
    status_id = None
    precent_type_id = None
    precent_item_type_id = None
    type_id = None

    @property
    def full_path(self):
        return f'{settings.FILES_STORE}{os.sep}{self.stored_file_name}' if self.stored_file_name else None

    def getKey(self):
        return self.key.hex().upper()

    # Зашифровать
    def encript(self, source_path=None):
        if self.full_path:
            if source_path:
                if not os.path.exists(source_path):
                    raise Exception(f'Заданый source_path : {source_path} не существует.')

            cipher = AES.new(self.key, AES.MODE_EAX)
            src = ''
            if (source_path):
                src = f'{source_path}{os.sep}{self.stored_file_name}.'
                self.logger.debug(f'Начало копирования {src} -> {self.full_path}.')
                shutil.copy2(src, self.full_path)
                self.logger.debug(f'Копирование завершено {src} -> {self.full_path}.')

            self.logger.debug(f'Начало чтения {src}')
            data = open(self.full_path, 'rb').read()
            ciphertext, tag = cipher.encrypt_and_digest(data)
            self.logger.debug(f'Чтение {src} завершено.')

            self.logger.debug(f'Начало шифрования {src}')
            file_out = open(f'{self.full_path}', 'wb')
            [file_out.write(x) for x in (cipher.nonce, tag, ciphertext)]
            self.logger.debug(f'Шифрование {src} завершено.')
            return self.key
        else:
            return None

    # Расшифровать
    def decrypt(self):
        if self.full_path:
            file_in = open(self.full_path, 'rb')

            nonce, tag, ciphertext = [file_in.read(x) for x in (16, 16, -1)]

            # let's assume that the key is somehow available again
            cipher = AES.new(self.key, AES.MODE_EAX, nonce)
            data = cipher.decrypt_and_verify(ciphertext, tag)
            path = f'{self.full_path}fordownload'
            res = open(path, 'wb')
            res.write(data)
            res.close()
            return path

    def zip(self):
        z = zipfile.PyZipFile(f'{self.full_path}.zip', 'w', zipfile.ZIP_DEFLATED, True, 2)
        z.write(self.full_path)
        z.close()

    def __init__(self, dictionary=dict(), key=None, stored_file_name=None, logger=None):
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

        if not settings.FILES_STORE:
            raise Exception('Не задан FILES_STORE.')

        if not os.path.exists(settings.FILES_STORE):
            raise Exception(f'Заданый FILES_STORE : {settings.FILES_STORE} не существует.')

        self.key = get_random_bytes(16)
        if key:
            self.key = key

        if stored_file_name:
            self.stored_file_name = stored_file_name

        if isinstance(dictionary, str):
            dictionary = json.loads(dictionary)

        if isinstance(dictionary, dict):
            for k, v in dictionary.items():
                setattr(self, k, v)
