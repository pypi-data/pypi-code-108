# coding=utf-8
from base import BaseModel
from lcyframe import yaml2py
from lcyframe import ServicesFindet
from lcyframe.beanstalk_server import BeanstalkWorker
from context import InitContext

config = InitContext.get_context()

tasks = BeanstalkWorker(**config)
yaml2py.impmodule(BaseModel, model_dir="model")
ServicesFindet(tasks, BaseModel)(config)
tasks.start()
