from log import Log
import pathlib
import os
import json
from collections import namedtuple
import pandas as pd
from MXException import *
from time import sleep

file_path = pathlib.Path(__file__).resolve()


def get_settings():
    settings_path = file_path.parent / 'settings.json'
    with open(settings_path) as settings_file:
        serialize_settings = settings_file.read()
    settings = json.loads(serialize_settings,
                          object_hook=lambda d: namedtuple('Settings', d.keys())(*d.values()))
    return settings


def get_query_result_file(query):
    query_json_path = file_path.parent / 'query.json'
    with open(query_json_path) as query_file:
        query_json = json.loads(query_file.read())
    return query_json[query]


class DBClient:
    def execute_DB_query(self, query, multi=False):
        return self.__execute_query(query, multi)

    def execute_ETL_query(self, query, multi=False):
        return self.__execute_query(query, multi)

    def __execute_query(self, query, multi):
        query_result_path = os.path.join(str(file_path.parent), get_query_result_file(query))
        result = pd.read_csv(query_result_path)
        sleep(1)
        return result


class EmailClient:
    __email_client = None

    def __init__(self):
        self.__email_count = 0

    @classmethod
    def get_instance(cls):
        if cls.__email_client is None:
            cls.__email_client = EmailClient()
        return cls.__email_client

    def send_email_notification(self, type, subject, message, isHtml=False, attachments=[]):
        if self.__email_count >= 3:
            raise MXTooManyRequestsError()
        if type.lower() == "success":
            type = 'Success'
        elif type.lower() == "failure":
            type = "Failure"
        else:
            result = False
        print('Email Starts')
        print('Type : ', type)
        print('Subject : ', subject)
        print('Message :', message)
        if len(attachments) > 0:
            print('Attachments : ', attachments)
        print('Email Ends')

        self.__email_count += 1


class LS:
    log = Log
    settings = get_settings()
    db = DBClient()
    email = EmailClient.get_instance()
