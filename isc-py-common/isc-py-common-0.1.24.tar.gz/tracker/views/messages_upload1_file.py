import logging
from tempfile import TemporaryFile

from django.core.files import File
from django.db import transaction

from crypto.models.upload_file import DSResponse_UploadFile
from isc_common.auth.models.user import User
from isc_common.common import uuid4
from isc_common.common.UploadItem import UploadItem
from isc_common.common.functions import Common
from isc_common.dropzone import Dz
from isc_common.http.RPCResponse import RPCResponseConstant

logger = logging.getLogger(__name__)


class DSResponse__Messages_UploadFile1(DSResponse_UploadFile):
    user = None

    def __init__(self, request):

        self.dz_dictionary = Dz(request.POST)

        self.host = self.dz_dictionary.host
        self.port = self.dz_dictionary.port
        self.channel = self.dz_dictionary.ws_channel

        self.file = request.FILES.get('file')
        self.user = User.objects.get(id=self.dz_dictionary.user_id)

        setattr(self.dz_dictionary, 'real_file_name', self.file.name)
        setattr(self.dz_dictionary, 'stored_file_name', self.dz_dictionary.dzuuid)
        setattr(self.dz_dictionary, 'file_size', self.dz_dictionary.dztotalfilesize)
        setattr(self.dz_dictionary, 'file_mime_type', self.file.content_type)
        setattr(self.dz_dictionary, 'guid', uuid4())

        self.handle_uploaded_file()

    @property
    def first_chunk(self):
        res = int(self.dz_dictionary.dzchunkindex) == 0
        return res

    @property
    def last_chunk(self):
        res = int(self.dz_dictionary.dztotalchunkcount) == int(self.dz_dictionary.dzchunkindex) + 1
        return res

    def handle_uploaded_file(self):
        try:

            item = UploadItem(dictionary=self.dz_dictionary.__dict__)

            def load_str(pers):
                return f'Загружено: {self.file.name}: {pers} %'

            with TemporaryFile() as src:
                src.seek(int(self.dz_dictionary.dzchunkbyteoffset))
                src.write(self.file.read())

                pers = round((int(self.dz_dictionary.dzchunkindex) * 100) / int(self.dz_dictionary.dztotalchunkcount), 2)
                if self.last_chunk:
                    pers = 100

                logger.debug(f'{load_str(pers)}, шаг : {int(self.dz_dictionary.dzchunkindex) + 1} из {self.dz_dictionary.dztotalchunkcount}')

                if self.last_chunk:
                    logger.debug(f'Загружен файл: {item.real_file_name}')

                    logger.debug(f'Запись временного файла.')
                    with open(item.full_path, 'w+b') as destination:
                        src.seek(0)
                        destination.write(src.read())
                    logger.debug(f'Запись временного файла выполнена.')

                    logger.debug(f'Запись: {item.full_path}.')
                    with open(item.full_path, 'rb') as src:
                        fileObj = File(src)

                        with transaction.atomic():
                            from tracker.models.messages_files import Messages_files
                            messages_file = Messages_files.objects.create(
                                attfile=fileObj,
                                file_store=self.get_path(fileObj.name),
                                format=item.file_format,
                                mime_type=item.file_mime_type,
                                real_name=item.real_file_name,
                                size=item.file_size,
                            )

                            url = f'logic/Messages_files/Download/{messages_file.id}/?host={self.host}&port={self.port}&ws_channel=common_{self.user.username}'
                            message = f'<p/><div>Выложен файл: <a href="{url}" target="hiddenframe"><strong>{item.real_file_name}</strong></a>   {Common.get_size_file_str(item.file_size)}</div><p/>'

                            face = "times new roman,times,serif"
                            size = 4

                            message = f'<font face ="{face}" size="{size}">{message}</font>'

                            logger.debug(f'Запись: {item.real_file_name} ({fileObj.name}) завершена.')

                            self.remove(item.full_path)
                            logger.debug(f'Удаление: {item.full_path} завершено.')

                    self.response = dict(response=dict(data=dict(message=message, id=messages_file.id)), status=RPCResponseConstant.statusSuccess)

        except Exception as e:
            raise e
