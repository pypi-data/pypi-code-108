# -*- coding: utf-8 -*-
from rer.ufficiostampa.interfaces import ISendHistoryStore
from rer.ufficiostampa.restapi.services.common import DataGet
from rer.ufficiostampa.restapi.services.common import DataCSVGet
from rer.ufficiostampa.restapi.services.common import DataClear


class SendHistoryGet(DataGet):
    store = ISendHistoryStore


class SendHistoryCSVGet(DataCSVGet):
    store = ISendHistoryStore
    type = "history"
    columns = [
        "status",
        "type",
        "date",
        "completed_date",
        "recipients",
        "channels",
        "title",
        "number"
    ]


class SendHistoryClearGet(DataClear):
    store = ISendHistoryStore
