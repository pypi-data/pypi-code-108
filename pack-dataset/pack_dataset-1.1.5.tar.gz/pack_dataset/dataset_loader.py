import os
import pymssql
import pandas as pd
from custom_exception import *
import hvac
import json


class GetterData:
    """
    Основной класс обработчик и загрузчик данных
    """

    def __init__(self):
        self.connection = None
        self.connect_data = self.get_connect_data()
        try:
            self.settings = self.read_settings()
        except Exception:
            print('Неудалось найти настроечный файл, пожалуйста создайте его прежде чем начать работу!')
            exit()

    def read_settings(self):
        """
        Функция чтения файла настройки
        Returns
        ---------
            settings: dict
                Словарь содержащий в себе компоненты необходимые для выгрузки данных
        """
        with open("settings.json") as file:
            settings = json.load(file)
        return settings

    def write_settings(self, prefix_login='', url='', cert_vault_tls='', cert_vault_key='', cert_vault_verify=''):
        """
        Функция создания файла настроек

        Parameters
        ------------
            prefix_login: str
                Префикс для логина (если не требуется добавьте поле и передайте пустую строку)
            url: str
                Url для подключения с использованием секретного токена
            cert_vault_tls: str
                Путь до секретного сертификата
            cert_vault_key: str
                Путь до ключа сертификата
            cert_vault_verify: str
                Путь до верификации сертификата
        """
        settings_to_json = {'prefix_login': prefix_login,
                            'url': url,
                            'cert_vault_tls': cert_vault_tls,
                            'cert_vault_key': cert_vault_key,
                            'cert_vault_verify': cert_vault_verify, }

        with open('settings.json', 'w') as file:
            json.dump(settings_to_json, file)

    def get_connect_data(self):
        """
        Функция для получения данных для подключения к базе
        Returns
        ---------
            connect_data: dict
                Словарь содержащий данные для подключения к базе данных
        """
        connect_data = {}
        try:
            connect_data_raw = os.environ.get(
                filter(lambda x: x.startswith("DATASET") and x.endswith("PATH"), os.environ).__next__())
            for pair in connect_data_raw.split(";")[:-1]:
                k, v = pair.split("=")
                connect_data[k.lower()] = v
        except Exception:
            print("Не удалось считать данные для подключения в автоматическом режиме введите их пожалуйста вручную!")
        return connect_data

    def connect_to_db_with_login(self, login, password):
        """
        Функция для подключения к базе данных с использованием логином и пароля

        Parameters
        ------------
            login: str
                Логин для подключения к базе данных
            password: str
                Пароль для подключения к базе данных
        Raises
        -------------
            ConnectException
                Исключение, вызываемое при отсутствии данных для подключения к базе (сервер, база данных, схема, таблица)
        """
        if len(self.connect_data) > 0:
            self.connect_data['username'] = self.settings['prefix_login'] + login
            self.connect_data['password'] = password
            self.connection = pymssql.connect(self.connect_data["server"],
                                              self.connect_data["username"],
                                              self.connect_data["password"],
                                              self.connect_data["database"])
        else:
            raise ConnectException

    def connect_to_db_with_token(self, vault_token, vault_secret_engine, vault_path):
        """
        Функция для подключения к базе данных с использованием библиотеки hvac

        Parameters
        ------------
            vault_token: str
                Vault токен
            vault_secret_engine: str
                Названиие используемого Secret Engine
            vault_path: str
                Путь до секрета в Vault
        Raises
        -------------
            ConnectException
                Исключение, вызываемое при отсутствии данных для подключения к базе (сервер, база данных, схема, таблица)
        """
        if len(self.connect_data) > 0:

            cli = hvac.Client(url=self.settings['url'],
                              token=vault_token,
                              cert=(self.settings["cert_vault_tls"], self.settings["cert_vault_key"]),
                              verify=self.settings["cert_vault_verify"])
            if cli.is_authenticated():
                creds = cli.secrets.kv.v2.read_secret_version(mount_point=vault_secret_engine, path=vault_path).get(
                    "data").get("data")

                login = creds.get('username')
                password = creds.get('password')
                self.connect_data['username'] = self.settings['prefix_login'] + login
                self.connect_data['password'] = password
                self.connection = pymssql.connect(self.connect_data["server"],
                                                  self.connect_data["username"],
                                                  self.connect_data["password"],
                                                  self.connect_data["database"])
        else:
            raise ConnectException

    def get_data_weather(self, row=None):
        """
        Функция для получения набора данных погоды (не указывай ничего если необходимо выгрузить весь набор данных)

        Parameters
        ------------
            row: int
                Число строк в выгружаемом наборе данных
        Raises
        -------------
            ConnectException
                Исключение, вызываемое при несоответствии параметра строки на целочисленное число
        """
        if (row is not None) and (type(row) == int) and (row > 0):
            sql_query = f"SELECT TOP {row} * FROM [{self.connect_data['database']}].[{self.connect_data['schema']}].[{self.connect_data['table']}]"
        elif type(row) != int or row < 0:
            raise RowException
        else:
            # Пока 35к как потолок, иначе кернел валится
            sql_query = f"SELECT TOP 35000 * FROM [{self.connect_data['database']}].[{self.connect_data['schema']}].[{self.connect_data['table']}]"
        dataset = pd.read_sql(sql_query, self.connection)
        return dataset
