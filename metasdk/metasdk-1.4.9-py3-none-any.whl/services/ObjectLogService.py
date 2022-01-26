import json


class ObjectLogService:
    """
    Служба журналирования логов по объектам
    """

    def __init__(self, app):
        """
        :type app: metasdk.MetaApp
        """
        self.__app = app
        self.__options = {}

    def log(self, record):
        """
        Делает запись по объекту в журнале
        """
        record['dispatcher'] = self.__app.dispatcher_name
        if 'value' in record and record['value']:
            if not isinstance(record['value'], dict):
                raise ValueError("ObjectLogService expected dict in log record value field")
            record['jsonValue'] = json.dumps(record['value'])
            record.pop('value')
        body_value = {
            "record": record
        }
        return self.__app.native_api_call('object-log', 'log', body_value, self.__options, False, None, False, http_path="/api/meta/v1/", http_method='POST')
