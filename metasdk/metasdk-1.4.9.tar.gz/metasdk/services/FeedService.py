import json
from tempfile import NamedTemporaryFile

SOURCE_FORMAT_EXTENSION = {
    'CSV': '.csv',
    'TSV': '.tsv',
    'JSON_NEWLINE': '.json'
}


class FeedService:
    def __init__(self, app):
        """
        :type app: metasdk.MetaApp
        """
        self.__app = app
        self.__options = {}
        self.__data_get_cache = {}
        self.__data_get_flatten_cache = {}
        self.__metadb = app.db("meta")
        self.__media = app.MediaService
        self.__starter = app.StarterService

    def get_feed(self, datasource_id):
        """
        Получение настроек для фида
        :param datasource_id: идентификатор фида
        :return: FeedDataSource
        """
        info = self.__metadb.one(
            """
            SELECT to_json(ds) as datasource
                 , to_json(fc) as connector
                 , to_json(fct) as connector_type
                 , to_json(ctp) as connector_type_preset
                 , json_build_object('email', u.email, 'full_name', u.full_name) as author_user
              FROM meta.feed_datasource ds
              LEFT JOIN meta.feed_connector fc 
                     ON fc.id=ds.connector_id
              LEFT JOIN meta.feed_connector_type fct 
                     ON fct.id=fc.connector_type_id
              LEFT JOIN meta.feed_connector_type_preset ctp 
                     ON ctp.id=ds.connector_type_preset_id
              LEFT JOIN meta.user_list u 
                     ON u.id=ds.author_user_id
             WHERE ds.id = :datasource_id::uuid
            """,
            {"datasource_id": datasource_id}
        )
        return FeedDataSource(**info)

    def get_data(self, datasource, callback):
        """
        Сохранение медиафайла
        :param task:
        :param media_metadata:
        :param file_suffix:
        :param callback:
        :return:
        """
        task = self.__app.worker.current_task
        media_metadata = datasource.connector_type_preset['preset_data']['media_metadata']
        result_data = task['result_data']
        tmp_file = NamedTemporaryFile(delete=False, suffix=SOURCE_FORMAT_EXTENSION.get(media_metadata['sourceFormat']))
        self.__app.log.info("Открываем файл", {"filename": tmp_file.name})
        with open(tmp_file.name, 'wb') as f:
            callback(f)

        self.__app.log.info("start media upload")

        result_data['stage_id'] = "persist_media_file"
        self.__starter.update_task_result_data(task)
        result = self.__media.upload(open(tmp_file.name), {
            "ttlInSec": 60 * 60 * 24,  # 24h
            "entityId": 2770,
            "objectId": task.get('data', {}).get("ds_id"),
            "info": {"metadata": media_metadata}
        })

        result_data['stage_id'] = "generate_media_finish"
        result_data['media_id'] = result['id']
        self.__starter.update_task_result_data(task)

        return result

    def datasource_process(self, datasource_id):
        """
        deprecated
        Запускает настроенные обработки в фиде
        :param datasource_id: uuid
        """
        # TODO Выпилить потом класс используется для другого
        # TODO без applicationId не выбираются поля сущностей. Подумать на сколько это НЕ нормально
        response = self.__app.native_api_call('feed', 'datasource/' + datasource_id + '/process?applicationId=1', {},
                                              self.__options, False, None, False, http_method="POST")
        return json.loads(response.text)


class FeedDataSource:
    """
    Класс хранения данных по коннектору
    """

    def __init__(self, datasource, author_user, connector, connector_type, connector_type_preset):
        self.datasource = datasource
        self.author_user = author_user
        self.connector = connector
        self.connector_type = connector_type
        self.connector_type_preset = connector_type_preset
