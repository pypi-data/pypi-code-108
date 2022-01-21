# coding=utf-8
import os, sys
from context import InitContext
from lcyframe.app import App
import platform

"""
定时任务
"""
config = InitContext.get_context()

config["wsgi"]["port"] = 8181 if len(sys.argv) == 1 else int(
    sys.argv[1])  # config["wsgi"]["port"] if len(sys.argv) == 1 else int(sys.argv[1])
config["wsgi"]["debug"] = False
config["wsgi"]["logging_debug"] = "debug"

config["api_docs"]["auto_generate"] = False
config["mqtt_config"]["client_id_name"] = "crontab_%s_%s" % (platform.node(), config["wsgi"]["port"])


config["task"] = [
    (CrontabModel.dosomething, 8000),  # ******
]

if __name__ == "__main__":
    app = App(**config)
    app.start()
