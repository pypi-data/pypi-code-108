from .config import Config
from .http import Http
from .mqtt import Mqtt
from .sql import Entry, Flow
import json

from sqlalchemy.sql.expression import true
from sqlalchemy import create_engine, Integer
from sqlalchemy.orm import sessionmaker

from pdb import set_trace as stop


class Service():
    default_config = {
            "ADDR": "127.0.0.1",
            "PORT": "10100",
            "WORKDIR": ".",
            "MQTT_ADDR": "localhost",
            "MQTT_PORT": 1883
        }

    def __init__(self, cfg: object, srv_name: str):
        self.config = Config(self.default_config)
        self.config.from_object(cfg)
        self.srv_name = srv_name
        
        # print('sqlite:///{0}/dm.db?charset=utf8'.format(self.config["WORKDIR"]))
        engine = create_engine('sqlite:///{0}/dm.db'.format(self.config["WORKDIR"]))
        Entry.__table__.create(engine, checkfirst=True)
        Flow.__table__.create(engine, checkfirst=True)
        self.sql = sessionmaker(bind=engine)()

        self.http = Http(self.config, self.srv_name, sql=self.sql)
        self.http.srv = self
        
        self.mqtt = Mqtt(self.config['MQTT_ADDR'], self.config['MQTT_PORT'])
        self.mqtt.srv = self

        self.devmodels = {}
        self.devs = {}

    def Bind(self, app):
        self.app = app
        self.app.srv = self
        self.http.Build()

    def AddDev(self, model):
        try:
            return self.app.AddDev(model)
        except Exception as e:
            return e
    
    def UpdateDev(self, model):
        try:
            return self.app.UpdateDev(model)
        except Exception as e:
            return e
    
    def DeleteDev(self, id):
        try:
            return self.app.DeleteDev(id)
        except Exception as e:
            return e
    
    def InitDev(self, model):
        try:
            return self.app.InitDev(model)
        except Exception as e:
            print(e)
            return str(e)

    def InitAllDevs(self):
        models = self.sql.query(Entry).all()
        flows = self.sql.query(Flow).all()
        try:
            for m in models:
                model = json.loads(m.content)
                self.devmodels[m.id] = model
                self.devs[m.id] = self.InitDev(model)
            if len(flows) > 0:
                flowModels = json.loads(flows[0].content)
                for f in flowModels:
                    self.devs[f['dev_id']].flow('add', srv_name=f['srv_name'], sub_topic=f['sub_topic'], pub_topic=f['pub_topic'], qos=f['qos'] )
        except Exception as e:
            print("[InitAllDevs error]:" + e)
            pass

    # def parse(self, model_str: str) -> object:

    def ReadProperty(self, key: str, content):
        print("Read property: " + key)
        try: # Service mode
            return getattr(self.app, key)
        except: # Protocol mode (need implementation)
            return self.app.ReadProperty(key, content) 
        
    def WriteProperty(self, key:str, content):
        print("Write property: " + key)
        print(content)
        try: # Service
            setattr(self.app, key, content)
        except: # Protocol
            return self.app.WriteProperty(key, content)

    def Execute(self, func_name:str, content = None):
        print("Execute function: " + func_name)
        if (content == None):
            return getattr(self.app, func_name)()
        else:
            print(content)
            if isinstance(content, str):
                return getattr(self.app, func_name)(**(json.loads(content)))
            elif isinstance(content, dict):
                return getattr(self.app, func_name)(**content)
            else:
                return "Content type is not supported"