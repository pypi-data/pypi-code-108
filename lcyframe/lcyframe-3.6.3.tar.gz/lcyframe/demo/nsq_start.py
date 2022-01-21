from lcyframe.nsq_server import NsqWorker
import os
from bson.objectid import ObjectId
from lcyframe import yaml2py
from base import BaseModel
from lcyframe import ServicesFindet
from context import InitContext


config = InitContext.get_context()
config["nsq_config"]["client_id_name"] = "nsq_works_" + str(ObjectId())


w = NsqWorker(**config)
yaml2py.impmodule(BaseModel, "model")
ServicesFindet(w, BaseModel)(config)
w.start()
