import json
import logging
import os
from tempfile import TemporaryFile

from crypto.models.upload_file import DSResponse_UploadFile
from django.conf import settings
from django.core.files import File
from django.db import transaction
from isc_common.common import SFTP, FILES_STORE_UNKNOWN_TYPE
from isc_common.common.UploadItem import UploadItem
from isc_common.dropzone import Dz
from isc_common.fields.files import make_REPLACE_FILE_PATH
from isc_common.http.DSResponse import JsonResponseWithException
from isc_common.models.image_types import Image_types
from isc_common.models.images import Images
from websocket import create_connection


logger = logging.getLogger(__name__)


class Common_UploadImage(DSResponse_UploadFile):
    def upload_image(self, request, delete_img_refs):

        self.dictionary = dict(id=request.GET.get('id'))

        self.dz_dictionary = Dz(request.POST)

        self.host = request.GET.get('host')
        self.port = request.GET.get('port')
        self.image_type_name = request.GET.get('image_type_name')
        self.keyImage = request.GET.get('keyImage')

        if self.image_type_name is None:
            raise Exception('Не задан параметр image_type_name.')
        if not self.port:
            self.port = 80
        self.channel = request.GET.get('ws_channel')
        self.file = request.FILES.get('upload_attatch')

        self.dictionary.update(dict(
            real_file_name=self.file.name,
            stored_file_name=self.dz_dictionary.dzuuid,
            file_size=int(self.dz_dictionary.dztotalfilesize),
            file_mime_type=self.file.content_type)
        )

        item = UploadItem(dictionary=self.dictionary)

        def load_str(pers):
            return f'Загружено: {pers} %'

        image_type, _ = Image_types.objects.get_or_create(code=self.image_type_name, keyimage=self.keyImage, defaults=dict(name=self.image_type_name))

        res = Images.objects.getOptional(
            size=item.file_size,
            real_name=item.real_file_name,
        )

        if res is not None:
            attfile = make_REPLACE_FILE_PATH(str(res.attfile))

            if isinstance(settings.FILES_STORE, str):
                ex = os.path.exists(attfile)
                if ex is False:
                    delete_img_refs(old_id=res.id)
                    res = None
            else:
                ssh_clients = settings.SSH_CLIENTS.client(settings.FILES_STORE)
                ex = ssh_clients.exists(attfile)
                if ex is False:
                    delete_img_refs(old_id=res.id)
                    res = None

        if res is None:
            with TemporaryFile() as src:
                src.seek(int(self.dz_dictionary.dzchunkbyteoffset))
                src.write(self.file.read())

                pers = round((int(self.dz_dictionary.dzchunkindex) * 100) / int(self.dz_dictionary.dztotalchunkcount), 2)
                if self.last_chunk:
                    pers = 100

                logger.debug(f'{load_str(pers)}, шаг : {int(self.dz_dictionary.dzchunkindex) + 1} из {self.dz_dictionary.dztotalchunkcount}')

                if self.last_chunk:
                    logger.debug(f'Загружен файл: {item.real_file_name}.')
                    logger.debug(f'Запись временного файла.')

                    with open(item.full_path, 'w+b') as destination:
                        src.seek(0)
                        destination.write(src.read())
                        logger.debug(f'Запись временного файла выполнена.')

                    logger.debug(f'Запись: {item.full_path}.')
                    with open(item.full_path, 'rb') as src:
                        src.seek(0)
                        fileObj = File(src)

                        if isinstance(settings.FILES_STORE, str):
                            file_store = os.path.abspath(settings.FILES_STORE)
                        elif isinstance(settings.FILES_STORE, dict) and settings.FILES_STORE.get('mode') == SFTP:
                            file_store = settings.FILES_STORE.get('PATH')
                        else:
                            raise Exception(FILES_STORE_UNKNOWN_TYPE)

                        res = Images.objects.create(
                            attfile=fileObj,
                            file_store=file_store,
                            format=item.file_format,
                            mime_type=item.file_mime_type,
                            size=item.file_size,
                            real_name=item.real_file_name,
                        )

                        ws = create_connection(f"ws://{self.host}:{self.port}/ws/{self.channel}/")
                        ws.send(json.dumps(dict(id=item.id, item_id=res.id, type="uploaded")))
                        ws.close()

                    logger.debug(f'Запись: {item.real_file_name} ({fileObj.name}) завершена.')

                    self.remove(item.full_path)
                    logger.debug(f'Удаление: {item.full_path} завершено.')

        return res, image_type, item.id

    @property
    def last_chunk(self):
        res = int(self.dz_dictionary.dztotalchunkcount) == int(self.dz_dictionary.dzchunkindex) + 1
        return res


@JsonResponseWithException()
class DSResponse_UploadImage(Common_UploadImage):
    def __init__(self, request):
        self.upload_image(request=request)


@JsonResponseWithException()
class DSResponse_CommonUploadImage(Common_UploadImage):
    def __init__(self, request, model, image_model, field_main_model=''):
        with transaction.atomic():
            file = request.FILES.get('upload_attatch')
            if file is not None:
                image, type, id = self.upload_image(request=request)

                main_model = eval(f"model.objects.get( id={id} ){f'.{field_main_model}' if field_main_model else ''}")
                if main_model is None:
                    raise Exception(f'Для field_main_model {field_main_model} не найдено main_model')

                main_model_image = image_model.objects.getOptional(main_model=main_model, image=image, type=type, deleted_at__isnull=False)

                if main_model_image is not None:
                    main_model_image.soft_restore()
                    main_model_image.save()
                else:
                    main_model_image = image_model.objects.create(main_model=main_model, type=type, image=image)

                image_model.objects.filter(main_model=main_model, type=type, deleted_at__isnull=True).exclude(id=main_model_image.id).soft_delete()

                logger.debug(f'Created: {main_model_image}')
