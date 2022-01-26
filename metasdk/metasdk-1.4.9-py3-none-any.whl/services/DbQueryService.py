import json

import shutil


class DbQueryService:
    def __init__(self, app, options):
        """
        :type app: metasdk.MetaApp
        """
        self.__app = app
        self.__options = options

    def schema_data(self, configuration):
        params = {"configuration": json.dumps(configuration)}
        dr = self.__app.native_api_call('db', 'schema-data', params, self.__options, True)
        return json.loads(dr.text)

    def upload_data(self, file_descriptor, configuration):
        multipart_form_data = {
            'file': file_descriptor
        }
        params = {"configuration": json.dumps(configuration)}
        dr = self.__app.native_api_call('db', 'upload-data', params, self.__options, True, multipart_form_data)
        return json.loads(dr.text)

    def download_data(self, configuration, output_file):
        params = {"configuration": json.dumps(configuration)}
        response = self.__app.native_api_call('db', 'download-data', params, self.__options, True, None, True)
        with open(output_file, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response

    def batch_update(self, command, rows):
        """
        Для массовой вставки умеренных объемов 1-5к записей за вызов

        :param command: SQL insert or updtae
        :param rows: list of dict
        :return: dict
        """
        request = {
            "database": {
                "alias": self.__options['dbAlias']
            },
            "batchUpdate": {
                "command": command,
                "rows": rows,
                "shardKey": self.__options.get('shardKey'),
            }
        }
        dr = self.__app.native_api_call('db', 'batch-update', request, self.__options, False)
        return json.loads(dr.text)

    def update(self, command, params=None):
        """
        Запросы на INSERT, UPDATE, DELETE и пр. не возвращающие результата должны выполняться через этот метод
        Исключение такие запросы с RETURNING для PostgreSQL

        :param command: SQL запрос
        :param params: Параметры для prepared statements
        :rtype: object DataResult
        """
        request = {
            "database": {
                "alias": self.__options['dbAlias']
            },
            "dbQuery": {
                "command": command,
                "parameters": params,
                "shardKey": self.__options.get('shardKey'),
            }
        }
        dr = self.__app.native_api_call('db', 'update', request, self.__options, False)
        return json.loads(dr.text)

    def query(self, command, params=None, max_rows=0):
        """
        Выполняет запрос, который ОБЯЗАТЕЛЬНО должен вернуть результат.
        Если вам надо сделать INSERT, UPDATE, DELETE или пр. используйте метод update
        или возвращайте результата через конструкцию RETURNING (нет в MySQL)

        > db.query('SELECT * FORM users WHERE id=:id', {"id":MY_USER_ID})

        :param command: SQL запрос
        :param params: Параметры для prepared statements
        :param max_rows: Если запрос вернет строк больше, чем указано в max_rows, то будет ошибка. Если равно нулю, действуют стандартные ограничения (50000)
        :rtype: object DataResult
        """
        request = {
            "database": {
                "alias": self.__options['dbAlias']
            },
            "dbQuery": {
                "maxRows": max_rows,
                "command": command,
                "parameters": params,
                "shardKey": self.__options.get('shardKey'),
            }
        }
        dr = self.__app.native_api_call('db', 'query', request, self.__options, False)
        return json.loads(dr.text)

    def one(self, command, params=None):
        """
        Возвращает первую строку ответа, полученного через query

        > db.query('SELECT * FORM users WHERE id=:id', {"id":MY_USER_ID})

        :param command: SQL запрос
        :param params: Параметры для prepared statements
        :rtype: dict
        """
        dr = self.query(command, params)
        if dr['rows']:
            return dr['rows'][0]
        else:
            return None

    def all(self, command, params=None):
        """
        Возвращает строки ответа, полученного через query

        > db.query('SELECT * FORM users WHERE id=:id', {"id":MY_USER_ID})

        :param command: SQL запрос
        :param params: Параметры для prepared statements
        :rtype: list of dict
        """
        dr = self.query(command, params)
        return dr['rows']
