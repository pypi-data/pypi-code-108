#  (C) Copyright IBM Corp. 2021.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import json
import os

from .globalization_util import GlobalizationUtil
import ibm_watson_machine_learning.messages


def get_message_dict(locale):
    file_name = "messages_" + locale + ".json"
    message_dict = {}
    path = os.path.dirname(ibm_watson_machine_learning.messages.__file__)
    messages = []
    # try to load the respective json file for the locale
    try:
        with open(os.path.join(path, file_name)) as f:
            messages = json.loads(f.read())
    # load the english dictionary if the json file for the locale doesn't exist
    except:
        try:
            return get_message_dict("en")
        except:
            raise Exception(
                "An error occurred while trying to load the message json file for the {} locale. "
                "Make sure the json file exists and is located in the correct folder.".format(locale))

    messages_list = [{item["code"]:item["message"]} for item in messages]
    for i in range(len(messages_list)):
        message_dict.update(messages_list[i])
    return message_dict


MESSAGE_DICT = get_message_dict(GlobalizationUtil.get_language())


def replace_args_in_message(message, *args):
    if args:
        varss = []
        for x in args:
            if x is not None and type(x) is not Exception:
                varss.append(x)
        if '{0}' in message:
            message = message.format(*varss)
        else:
            message = message % tuple(varss)
    return message


class Messages:

    @classmethod
    def get_message(cls, *args, message_id):
        message = MESSAGE_DICT.get(message_id)

        if args and message:
            message = replace_args_in_message(message, *args)

        return message
