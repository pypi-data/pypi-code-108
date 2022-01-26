import json


class MediaService:
    def __init__(self, app):
        """
        :type app: metasdk.MetaApp
        """
        self.__app = app
        self.__options = {}

    def persist_one(self, file_base64_content, filename, extension, mime, is_private=True):
        """
        Загружает файл в облако
        :type origin: string Принимает значения ROBOT, USER
        """
        return self.__app.api_call("MediaService", "persist_one", locals(), {})

    def upload(self, file_descriptor, settings):
        """
        Загружает файл в облако
        :param file_descriptor: открытый дескриптор
        :param settings: настройки загрузки
        :rtype: requests.Response
        """
        multipart_form_data = {
            'file': file_descriptor
        }
        params = {"settings": json.dumps(settings)}
        dr = self.__app.native_api_call('media', 'upload', params, self.__options, True, multipart_form_data, False, http_path="/api/meta/v1/", http_method='POST',
                                        connect_timeout_sec=60 * 10)
        return json.loads(dr.text)

    def download(self, media_id, as_stream=False):
        """
        Скачивает указанный файл
        :param media_id: string
        :rtype: requests.Response
        """
        response = self.__app.native_api_call('media', 'd/' + media_id, {}, self.__options, False, None, as_stream, http_path="/api/meta/v1/", http_method='GET')
        return response

    def info(self, media_id):
        """
        Получить информацию по файлу
        :param media_id:
        :rtype: requests.Response
        """
        dr = self.__app.native_api_call('media', 'i/' + media_id, {}, self.__options, False, None, False, http_path="/api/meta/v1/", http_method='GET')
        return json.loads(dr.text)
