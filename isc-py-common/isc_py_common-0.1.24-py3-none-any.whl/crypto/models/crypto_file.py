import logging
import os
from os.path import getsize
from shutil import copyfile

from django.conf import settings
from django.core.files import File
from django.db.models import BinaryField, BigIntegerField, CharField, TextField
from django.forms import model_to_dict
from isc_common import delAttr
from isc_common.common import SFTP, FILES_STORE_UNKNOWN_TYPE
from isc_common.common.UploadItemEx import UploadItemEx
from isc_common.fields.files import FileFieldEx, make_REPLACE_FILE_PATH
from isc_common.fields.name_field import NameField
from isc_common.http.DSRequest import DSRequest
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager, CommonManagetWithLookUpFieldsQuerySet
from isc_common.models.audit import AuditModel

logger = logging.getLogger(__name__)


class CryptoQuerySet(CommonManagetWithLookUpFieldsQuerySet):

    def delete(self):
        for item in self:
            Crypto_file.remove_file(item=item)
        return super().delete()


class CryptoManager(CommonManagetWithLookUpFieldsManager):
    def createFromRequest(self, request, function=None):
        request = DSRequest(request=request)
        data = request.get_data()
        _data = data.copy()
        for key in data:
            if key.find('__') != -1:
                delAttr(_data, key)
        delAttr(_data, 'form')
        if data.get('id') or not data.get('real_name'):
            delAttr(_data, 'id')
            res = super().filter(id=data.get('id')).update(**_data)
            res = model_to_dict(res[0])
            delAttr(res, 'attfile')
            delAttr(res, 'form')
            data.update(res)
        return data

    def updateFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()
        delAttr(data, 'form')
        super().filter(id=request.get_id()).update(**data)
        return data

    def get_queryset(self):
        return CryptoQuerySet(self.model, using=self._db)


class Crypto_file(AuditModel):
    attfile = FileFieldEx(verbose_name='Файл', max_length=255)
    file_store = CharField(verbose_name='Каталог хранения файла', max_length=255, null=True, blank=True)
    format = NameField(verbose_name='Формат файла')
    key = BinaryField(max_length=200, null=True, blank=True)
    mime_type = NameField(verbose_name='MIME тип файла файла')
    real_name = TextField(verbose_name='Первоначальное имя файла', db_index=True, )
    size = BigIntegerField(verbose_name='Размер файла', default=None)

    object = CryptoManager()

    @property
    def olnly_real_file_name(self):
        ls = self.real_name.split('\\')
        return ls[len(ls) - 1]

    @classmethod
    def exists(cls, filename):
        res = os.path.exists(make_REPLACE_FILE_PATH(filename))
        if res is False:
            logger.debug(f'file: {filename} not exists.')
        return filename, res

    @classmethod
    def check_file(cls, attfile):
        attfile = make_REPLACE_FILE_PATH(str(attfile))
        logger.debug(f'check_file: {attfile}')

        if attfile is None or attfile == '':
            logger.debug(f'file: {attfile} not exists')
            return attfile, False
        else:
            filename = attfile

            if isinstance(settings.FILES_STORE, str):
                _, exists = cls.exists(filename)
                if exists is False or getsize(filename) == 0:
                    logger.debug(f'file: {attfile} not exists')
                    return filename, False

            elif isinstance(settings.FILES_STORE, dict) and settings.FILES_STORE.get('mode') == SFTP:
                ssh_client = settings.SSH_CLIENTS.client(settings.FILES_STORE)
                res = ssh_client.exists(filename)
                if res is False or ssh_client.getsize(filename) == 0:
                    logger.debug(f'file: {attfile} not exists')
                    return filename, False
            else:
                raise Exception(FILES_STORE_UNKNOWN_TYPE)

            logger.debug(f'file: {attfile} exists')
            return filename, True

    @classmethod
    def remove_file(cls, item):
        old_file_store = item.file_store
        file_path = item.attfile.name

        if old_file_store:
            if isinstance(settings.FILES_STORE, str):
                file_path = file_path.replace(old_file_store, settings.FILES_STORE)
            elif isinstance(settings.FILES_STORE, dict) and settings.FILES_STORE.get('mode') == SFTP:
                file_path = file_path.replace(old_file_store, settings.FILES_STORE.get('PATH'))
            else:
                raise Exception(FILES_STORE_UNKNOWN_TYPE)

        if isinstance(settings.REPLACE_FILE_PATH, dict):
            for key, value in settings.REPLACE_FILE_PATH.items():
                file_path = file_path.replace(key, value)

        if file_path:
            if os.altsep:
                file_path = file_path.replace(os.altsep, os.sep)

            if isinstance(settings.FILES_STORE, str):
                os.remove(file_path)
            else:
                settings.SSH_CLIENTS.client(settings.FILES_STORE).remove(settings.FILES_STORE.get('PATH'))
            logger.debug(f'Removed file: {file_path}')

    @classmethod
    def copy_file(cls, uploadItemEx):

        if isinstance(settings.OLD_FILES, dict):
            ssh_client = settings.SSH_CLIENTS.client(settings.OLD_FILES)
            if ssh_client.exists(uploadItemEx.real_file_name):
                ssh_client.get(localpath=uploadItemEx.full_path, remotepath=uploadItemEx.real_file_name)
            else:
                if uploadItemEx.tmp_file_name is not None and os.path.exists(uploadItemEx.tmp_file_name):
                    copyfile(src=uploadItemEx.tmp_file_name, dst=uploadItemEx.full_path)
        else:
            if cls.exists(uploadItemEx.real_file_name):
                copyfile(src=uploadItemEx.real_file_name, dst=uploadItemEx.full_path)
            else:
                if uploadItemEx.tmp_file_name is not None and os.path.exists(uploadItemEx.tmp_file_name):
                    copyfile(src=uploadItemEx.tmp_file_name, dst=uploadItemEx.full_path)

        res = cls.objects.getOptional(real_name=uploadItemEx.real_file_name, size=uploadItemEx.file_size)

        if isinstance(settings.FILES_STORE, dict):
            if res is not None and str(res.attfile) != '' and settings.SSH_CLIENTS.client(settings.FILES_STORE).exists(str(res.attfile)):
                return res, False
        else:
            if res is not None and str(res.attfile) != '' and os.path.exists(str(res.attfile)):
                return res, False

        with open(uploadItemEx.full_path, 'rb') as src:
            fileObj = File(src)

            defaults = dict(
                attfile=fileObj,
                file_store=os.path.split(uploadItemEx.real_file_name)[0],
                format=uploadItemEx.file_format,
                mime_type=uploadItemEx.file_mime_type,
                real_name=uploadItemEx.real_file_name,
                size=uploadItemEx.file_size,
            )

            res, created = cls.objects.update_or_create(
                id=uploadItemEx.id,
                defaults=defaults
            )

        if uploadItemEx.tmp_file_name is not None and os.path.exists(uploadItemEx.tmp_file_name):
            if not os.path.isdir(uploadItemEx.tmp_file_name):
                os.remove(uploadItemEx.tmp_file_name)
            os.remove(uploadItemEx.full_path)

        return res, created

    @classmethod
    def get_action(cls, res, item):
        action = None
        if isinstance(settings.FILES_STORE, dict):
            exists = str(res.attfile) != ''
            if exists is True:
                exists = settings.SSH_CLIENTS.client(settings.FILES_STORE).exists(path=str(res.attfile))
        else:
            exists = os.path.exists(str(res.attfile))

        if res.size is None or res.size == 0 or not exists:
            action = 'create'
        elif res.size != item.file_size:
            action = 'update'
        return action

    @classmethod
    def create_update(cls, **kwargs):
        uploadItemEx = UploadItemEx(**kwargs)

        try:
            if uploadItemEx.id is not None:
                res = cls.objects.get(id=uploadItemEx.id)
                action = cls.get_action(res=res, item=uploadItemEx)
            else:
                if uploadItemEx.real_file_name is None:
                    raise Exception('Must be real_file_name or id')
                else:
                    res = cls.objects.get(real_name=uploadItemEx.real_file_name)

                action = cls.get_action(res=res, item=uploadItemEx)

            if action is not None:
                if action == 'update':
                    cls.remove_file(item=res)

                return cls.copy_file(uploadItemEx=uploadItemEx)
            else:
                return None, None

        except cls.DoesNotExist:
            return cls.copy_file(uploadItemEx=uploadItemEx)
        except Exception as ex:
            raise ex

    def __str__(self):
        return f"{self.real_name}"

    class Meta:
        abstract = True
