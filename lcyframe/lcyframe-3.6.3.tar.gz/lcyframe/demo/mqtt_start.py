from lcyframe.mqtt_server import MqttWorker
import os
from bson.objectid import ObjectId
from lcyframe import yaml2py
from base import BaseModel
from lcyframe import ServicesFindet
from context import InitContext


config = InitContext.get_context()
config["mqtt_config"]["client_id_name"] = "mqtt_works_" + str(ObjectId())
config["mqtt_config"]["client_role"] = "worker"

w = MqttWorker(**config)
yaml2py.impmodule(BaseModel, "model")
ServicesFindet(w, BaseModel)(config)
w.start()
