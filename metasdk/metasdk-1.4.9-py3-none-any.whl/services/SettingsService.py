import json


class SettingsService:
    def __init__(self, app):
        """
        :type app: metasdk.MetaApp
        """
        self.__app = app
        self.__options = {}
        self.__data_get_cache = {}
        self.__data_get_flatten_cache = {}

    def config_param(self, conf_alias, param):
        """
        Получает настройки с сервера, кеширует локально и дает простой интерфейс их получения
        :param conf_alias:
        :param param:
        :return:
        """
        data = self.data_get(conf_alias)
        flat_cache = self.__data_get_flatten_cache.get(conf_alias)
        if flat_cache is None:
            flat_cache = self.__flatten_dict(data, '', '.')
            self.__data_get_flatten_cache[conf_alias] = flat_cache
        if param not in flat_cache:
            raise KeyError("Key not found: " + conf_alias)
        return flat_cache.get(param)

    def data_get(self, conf_alias, data_only=True, use_cache=True):
        """
        Запрашивает данные по настройке
        :param data_only: Вернуть только данные без метаинформации
        :param conf_alias: Уникальный альяс конфига
        :param use_cache: Запросить один ра и далее работать с закешированной в памяти копией
        :return:
        """
        data = self.__data_get_cache.get(conf_alias)
        if not use_cache or data is None:
            response = self.__app.native_api_call('settings', 'data/get/' + conf_alias, {}, self.__options, False, None, False, http_path="/api/meta/v1/", http_method="GET")
            data = json.loads(response.text)
            self.__data_get_cache[conf_alias] = data

        if data_only:
            return data.get("form_data")
        else:
            return data

    def clear_cache(self):
        """
        Очистить локальный кеш
        """
        self.__data_get_cache = {}

    def __flatten_dict(self, dict_, parent_key, sep):
        # https://stackoverflow.com/questions/6027558/flatten-nested-python-dictionaries-compressing-keys
        items = []
        for k, v in dict_.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, dict):
                items.extend(self.__flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
