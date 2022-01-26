import json
from requests import Response


class DataResult:
    """
    Класс данных, полученных из Meta API
    Позволяет потоково получать данные по мере их поступления из api
    Служит для обработки больших массивов данных
    """

    def __init__(self, resp: Response):
        self.__resp = resp

        chunk_size = 1024*1024  # 1Mb

        # Если не указать chunk_size - падает после переезда в яндекс-облако с Incomplete byte read
        # http://crm.realweb.ru/browse/METAFEEDS-1281
        self.__rows_iter = self.__resp.iter_lines(chunk_size)

        self.columns = self.__line_unserialize(next(self.__rows_iter))

    def __iter__(self):
        for line in self.__rows_iter:
            yield self.__line_unserialize(line)
        self.__resp.close()

    def __line_unserialize(self, line_str):
        # IMPORTANT! orjson НЕ юзать, вызывает что-то тпа SegFault на некоторых данных
        return json.loads(line_str)


class DbService:
    def __init__(self, app):
        """
        :type app: metasdk.MetaApp
        """
        self.__app = app
        self.__options = {}

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

    def persist_query(self, configuration):
        params = {}
        params.update(configuration)
        dr = self.__app.native_api_call('db', 'persist-query', params, self.__options)
        return json.loads(dr.text)

    def stream_query(self, configuration):
        """
        Не сохраняет ничего и ни куда.
        Мета передает данные в output,
        а python client должен их быстро вычитывать и закрывать коннект.
        Также позволяет получать список колонок
        :param configuration: dict
        :return: DataResult
        """
        params = {}
        params.update(configuration)
        dr = self.__app.native_api_call('db', 'stream-query', params, self.__options, stream=True,
                                        request_timeout_sec=60 * 60 * 3)
        return DataResult(dr)
