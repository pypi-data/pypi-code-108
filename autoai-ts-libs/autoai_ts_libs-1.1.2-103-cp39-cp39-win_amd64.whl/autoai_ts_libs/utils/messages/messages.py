#
#    IBM Confidential
#    OCO Source Materials
#    [5737-H76, 5725-W78, 5900-A1R, 5737-L65]
#    (C) Copyright IBM Corp. 2020  All Rights Reserved.
#    The source code for this program is not published or otherwise divested of its trade secrets,
#    irrespective of what has been deposited with the U.S. Copyright Office.

import json
import os

from autoai_ts_libs.utils.messages.globalization_util import GlobalizationUtil
import autoai_ts_libs.utils.messages


def get_message_dict(locale):
    file_name = "messages_" + locale + ".json"
    message_dict = {}
    path = os.path.dirname(autoai_ts_libs.utils.messages.__file__)
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
                "Please ensure that the json file exists and is placed in the appropriate folder".format(locale))

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
