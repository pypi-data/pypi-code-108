import os
from lcyframe.mq_server import MqWorker
from lcyframe.libs import yaml2py
from base import BaseModel
from lcyframe import ServicesFindet
from context import InitContext

config = InitContext.get_context()

w = MqWorker(**config)
yaml2py.impmodule(BaseModel, model_dir="model")
ServicesFindet(w, BaseModel)(config)
w.start()