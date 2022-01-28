import logging
import os
import shutil
import zipfile

from Cryptodome.Cipher import AES
from django.conf import settings
from isc_common.common import SFTP, FILES_STORE_UNKNOWN_TYPE
from isc_common.json import StrToJson
from isc_common.number import TryToInt
from isc_common.oss.functions import get_tmp_dir


class UploadItem:
    id = None
    file_format = None
    file_mime_type = None
    file_size = None
    file_name = None
    real_file_name = None
    tmp_file_name = None
    tmp_dir_name = None
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
        if isinstance(settings.FILES_STORE, str):
            return f'{get_tmp_dir(os.path.abspath(settings.FILES_STORE))}{os.sep}{self.stored_file_name}' if self.stored_file_name else None
        else:
            return f'{get_tmp_dir()}{os.sep}{self.stored_file_name}' if self.stored_file_name else None

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

    def __init__(self, stored_file_name=None, key=None, logger=None, dictionary=None):
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

        if not settings.FILES_STORE:
            raise Exception('Не задан FILES_STORE.')

        if isinstance(settings.FILES_STORE, str):
            if not os.path.exists(settings.FILES_STORE):
                raise Exception(f'Заданный FILES_STORE : {settings.FILES_STORE} не существует.')
        elif isinstance(settings.FILES_STORE, dict) and settings.FILES_STORE.get('mode') == SFTP:
            if settings.FILES_STORE.get('PATH') is None:
                raise Exception('FILES_STORE не содержит параметр PATH')

            PATH = settings.FILES_STORE.get('PATH')
            res = settings.SSH_CLIENTS.client(settings.FILES_STORE).exists(PATH)

            if res is False:
                raise Exception(f'Заданный FILES_STORE (SFTP) : {PATH} не существует.')

        else:
            raise Exception(FILES_STORE_UNKNOWN_TYPE)

        if dictionary is not None and dictionary.get('key') is not None:
            self.key = dictionary.get('key')
        else:
            self.key = key

        if dictionary is not None and dictionary.get('stored_file_name') is not None:
            self.stored_file_name = dictionary.get('stored_file_name')
        else:
            self.stored_file_name = stored_file_name

        if isinstance(dictionary, str):
            dictionary = StrToJson(dictionary)

        if isinstance(dictionary, dict):
            for k, v in dictionary.items():
                setattr(self, k, TryToInt(v))
