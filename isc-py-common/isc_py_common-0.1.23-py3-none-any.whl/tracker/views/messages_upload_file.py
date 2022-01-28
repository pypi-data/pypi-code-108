import hashlib
import logging
from tempfile import TemporaryFile

from django.core.files import File
from django.db import transaction

from crypto.models.upload_file import DSResponse_UploadFile
from isc_common.auth.models.user import User
from isc_common.common import uuid5
from isc_common.common.UploadItem import UploadItem
from isc_common.common.functions import Common
from isc_common.dropzone import Dz
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.ws.webSocket import WebSocket
from tracker.models.messages import Messages
from twits import ChatResponseData
from twits.models.chat_user_user import Chat_user_user
from twits.models.chat_user_user_theme import Chat_user_user_theme
from twits.models.chat_users import Chat_users

logger = logging.getLogger(__name__)


class DSResponse__Messages_UploadFile(DSResponse_UploadFile):
    user = None

    def __init__(self, request):

        self.dz_dictionary = Dz(request.POST)

        self.host = self.dz_dictionary.host
        self.port = self.dz_dictionary.port
        self.channel = self.dz_dictionary.channel

        self.file = request.FILES.get('file')
        self.user = User.objects.get(id=self.dz_dictionary.user_id)

        setattr(self.dz_dictionary, 'real_file_name', self.file.name)
        setattr(self.dz_dictionary, 'stored_file_name', self.dz_dictionary.dzuuid)
        setattr(self.dz_dictionary, 'file_size', self.dz_dictionary.dztotalfilesize)
        setattr(self.dz_dictionary, 'file_mime_type', self.file.content_type)
        setattr(self.dz_dictionary, 'guid', uuid5())

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

                        def rec_message(item):
                            # host, port, ws_channel данные для передачи ошибки в случае ее возникновения
                            url = f'logic/Messages_files/Download/{item.messages_file.id}/?host={self.host}&port={self.port}&ws_channel=common_{self.user.username}'
                            message = f'<div>Выложен файл: <a href="{url}" target="hiddenframe"><strong>{item.real_file_name}</strong></a>   {Common.get_size_file_str(item.file_size)}</div><p/>'

                            face = "times new roman,times,serif"
                            size = 4

                            message = f'<font face ="{face}" size="{size}">{message}</font>'

                            def _rec_message(id, item):
                                # if item.user_id != id:
                                if not isinstance(item.theme_ids, list):
                                    if isinstance(item.theme_ids, str):
                                        item.theme_ids = [int(item) for item in item.theme_ids.split(',')]
                                    else:
                                        item.theme_ids = [item.theme_ids]

                                for theme_id in item.theme_ids:
                                    message_obj = None
                                    try:
                                        chat_user_user_theme = Chat_user_user_theme.objects.get(theme_id=theme_id)
                                        if chat_user_user_theme.chat_user_user.user_reciver.id == id:
                                            message_obj, _ = Messages.objects.get_or_create(
                                                defaults=dict(
                                                    message=message,
                                                ),
                                                checksum=hashlib.md5(message.encode()).hexdigest(),
                                                guid=item.guid,
                                                state_id=item.message_state_new_id,
                                                theme_id=theme_id,
                                                to_whom_id=id,
                                                user_id=item.user_id,
                                            )
                                    except Chat_user_user_theme.DoesNotExist:
                                        message_obj, _ = Messages.objects.get_or_create(
                                            defaults=dict(
                                                message=message,
                                            ),
                                            checksum=hashlib.md5(message.encode()).hexdigest(),
                                            guid=item.guid,
                                            state_id=item.message_state_new_id,
                                            theme_id=theme_id,
                                            to_whom_id=id,
                                            user_id=item.user_id,
                                        )

                                    from tracker.models.messages_files_refs import Messages_files_refs
                                    if message_obj:
                                        Messages_files_refs.objects.get_or_create(messages_file=item.messages_file, message=message_obj)

                            type_chat, id = self.channel.split('_')

                            if type_chat == 'group':
                                for chat_users in Chat_users.objects.filter(chat_id=id):
                                    _rec_message(id=chat_users.user.id, item=item)

                            elif type_chat == 'tetatet':
                                for chat_user_user in Chat_user_user.objects.filter(common_id=id):
                                    _rec_message(id=chat_user_user.user_reciver.id, item=item)

                            message = ChatResponseData(
                                channel=self.channel,
                                date=item.date,
                                guid=item.guid,
                                message=message,
                                message_state_new_name=item.message_state_new_name,
                                type='uploaded_file',
                                user__color=item.user__color,
                                user__short_name=self.user.get_short_name,
                                user_id=self.user.id,
                            )
                            logging.debug(f'send_message: {message}')
                            WebSocket.send_message(host=self.host, port=self.port, channel=self.channel, message=message, logger=logger)

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

                            setattr(item, 'messages_file', messages_file)
                            rec_message(item=item)

                            logger.debug(f'Запись: {item.real_file_name} ({fileObj.name}) завершена.')

                            self.remove(item.full_path)
                            logger.debug(f'Удаление: {item.full_path} завершено.')

            self.response = dict(status=RPCResponseConstant.statusSuccess)

        except Exception as e:
            raise e
