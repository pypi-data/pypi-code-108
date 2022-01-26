import json

import shutil


class MetaqlService:
    def __init__(self, app):
        """
        :type app: metasdk.MetaApp
        """
        self.__app = app
        self.__options = {}

    def download_data(self, configuration, output_file):
        """
        Выполняет указанный в конфигурации запрос и отдает файл на скачивание
        :param configuration: Конфгурация запроса
        :param output_file: Место, куда надо скачать файл
        :return:
        """
        params = configuration
        response = self.__app.native_api_call('metaql', 'download-data', params, self.__options, False, None, True, http_path="/api/v1/meta/")
        with open(output_file, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response

    def get_schema(self, db_alias, entity):
        """
        Возвращает схему сущности:
            - Поля
        :param db_alias: Альяс БД
        :param entity: Альяс Сущности
        :return: dict
        """
        response = self.__app.native_api_call('metaql', 'schema/' + db_alias + '/' + entity, {}, self.__options, False, None, False, http_path="/api/v1/meta/", http_method="GET")
        return json.loads(response.text)
