import base64
import os
import logging
import re
import asyncio
import aiohttp

from .exception import *


class Secret:
    separator = "|"

    def __init__(self, token):
        self.logger = logging.getLogger(__name__)
        self.__list = self.get_secret_id()
        self.__token = token
        self.__secrets = {}
        self.__key = {}
        asyncio.get_event_loop().run_until_complete(self.request_secret())

    def get_secret_id(self):
        try:
            str = os.environ['YCSECRET']
            if str and str.strip():
                if self.check_str_secret(str):
                    chunks = list(filter(None, str.split(self.separator)))
                    return chunks
                else:
                    raise IncorrectLineException
            else:
                raise EmptyLineException
        except KeyError:
            self.logger.error('The variable YCSECRET is missing in the environment')
        except EmptyLineException:
            self.logger.error('Empty variable YCSECRET in the environment')
        except IncorrectLineException:
            self.logger.error('The YCSECRET variable string is not formatted correctly')
        except:
            self.logger.error('Unknown error')

    def check_str_secret(self, str):
        match = re.match(r'[a-z0-9' + self.separator + ']+$', str)
        return bool(match)

    async def get_request(self, session, url, item):

        headers = {"Accept": "application/json", "Authorization": f"Bearer {self.__token}"}

        async with session.get(url, headers=headers) as resp:
            try:
                json_body = await resp.json()
                if resp.status == 200:
                    return {item: json_body["entries"]}
                elif resp.status == 404:
                    raise BadStatusException(status=resp.status, message=json_body["message"])
                elif resp.status == 403:
                    raise BadStatusException(status=resp.status, message=json_body["message"])
            except BadStatusException as e:
                self.logger.error(
                    "Incorrect server response status "
                    f"status: {e.status}, "
                    f"message: {e.message}. "
                    "Check the existence of the secret and the rights of lockbox.payloadViewer or lockbox.admin"
                )

    async def request_secret(self):

        async with aiohttp.ClientSession() as session:
            tasks = []
            for item in self.__list:
                url = f"https://payload.lockbox.api.cloud.yandex.net/lockbox/v1/secrets/{item}/payload"
                tasks.append(asyncio.ensure_future(self.get_request(session, url, item)))

            list_secret = await asyncio.gather(*tasks)
            self.parse_data(list(filter(None, list_secret)))

    def parse_data(self, data):
        for item_secret in data:
            for key, list_key in item_secret.items():
                self.__secrets[key] = []
                for i, item in enumerate(list_key):
                    if item.get('binaryValue', False):
                        self.__key[item["key"]] = base64.b64decode(item["binaryValue"])
                        tmp = {
                            "key": item["key"],
                            "value": base64.b64decode(item["binaryValue"]),
                            "binaryValue": item["binaryValue"],
                            "typeValue": "binary"
                        }
                        self.__secrets[key].append(tmp)
                    else:
                        self.__key[item["key"]] = item["textValue"]
                        tmp = {
                            "key": item["key"],
                            "value": item["textValue"],
                            "textValue": item["textValue"],
                            "typeValue": "text"
                        }
                        self.__secrets[key].append(tmp)

    def get_key(self, key_name):
        if self.__key.get(key_name):
            return self.__key[key_name]
        else:
            return False

    def get_secret(self, secret_id):
        if self.__secrets.get(secret_id):
            return self.__secrets[secret_id]
        else:
            return False
