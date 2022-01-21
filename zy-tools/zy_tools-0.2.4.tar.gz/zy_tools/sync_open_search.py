# !/usr/bin/env python
# _*_coding: utf-8 _*_
# @Time: 2019/11/14 15:08
# @Author: "John"
import json
import uuid

import requests
import urllib3

urllib3.disable_warnings()


def sync_open_search(pid, db, collection, service_address, topic='TweOpensearch', is_sandbox=True):
    """

    :param pid:
    :param db:
    :param collection:
    :param service_address:
    :param topic: default for TweOpensearch
    :param is_sandbox: default for sandbox，not sync openSearch
    :return:
    """
    if is_sandbox:
        print(f"It is a test, not sync openSearch: pid:{pid}。")
        return

    headers = {"Content-type": "application/json; charset=UTF-8", "Accept": "application/json"}

    msg = {
        "topic": topic,
        "traceID": str(uuid.uuid1()).replace('-', ''),
        "msgData": {
            "mongodb": db,
            "collection": collection,
            "primaryKey": "PID",
            "primaryValue": pid.strip(),
            "isNew": 0
        }
    }

    resp = requests.post(service_address, headers=headers, data=json.dumps(msg))
    if resp.json().get("success"):
        return 1
