# coding=utf-8
import sys, os
from bson.objectid import ObjectId
from base import BaseModel
from lcyframe import yaml2py
from lcyframe import ServicesFindet
from lcyframe.libs.singleton import CeleryCon
from lcyframe.celery_server import CeleryWorker
from context import InitContext

# args = [item.split("=")[-1] for item in sys.argv if item.startswith("--config")]
sys.argv = sys.argv[:1]
config = InitContext.get_context()

tasks = CeleryWorker(**config)
yaml2py.impmodule(BaseModel, "model")       # 换为载入model父类，切worker的函数继承了model父类，所以可以使用所有的model子类
ServicesFindet(tasks, BaseModel)(config)    # 获取全站所有连接库，赋值给BaseModel，继承了BaseModel的worker内，含有mqtt生产者连接，可以使用生产者创建新的任务
app = CeleryCon._app                        # 命令行模式运行：celery -A celery_start worker --loglevel=info --pool=eventlet --concurrency=10 -Qapp_queue


if __name__ == "__main__":                  # Debug调试模式启动
    tasks.app = app
    tasks.start()
