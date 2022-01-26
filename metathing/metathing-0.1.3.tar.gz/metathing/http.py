#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# 增/删/改/查/获取所有

# POST: {srv-name}/models
# DELETE: {srv-name}/models/{instID}
# POST: {srv-name}/models/{instID}
# GET: {srv-name}/models/{instID}
# GET: {srv-name}/models

from tornado.web import Application,RequestHandler
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
import json
from pdb import set_trace as stop

from .sql import Entry

from tornado.escape import json_decode

class CustomHandler(RequestHandler):

    def get_argument(self, id:str):
        if self.request.headers['Content-Type'] == 'application/json':
            args = json_decode(self.request.body)
            return args[id]
        return super(CustomHandler, self).get_argument(id)


# # SQLITE
# class Entry(Base):
#     __tablename__ = 'model'
#     id = Column(String, primary_key=True, index=True, unique=True)
#     content = Column(String)
#     def __repr__(self):
#         return json.dumps({
#             "id": self.id,
#             "content": self.content
#         })

class Http():
    def __init__(self, config: dict, srv_name: str, sql=None) -> None:
        self.config = config
        self.srv_name = srv_name
        self.sql = sql
        self.srv = None

        # print('sqlite:///{0}/dm.db'.format(self.config["WORKDIR"]))
        # engine = create_engine('sqlite:///{0}/dm.db'.format(self.config["WORKDIR"]))
        # Entry.__table__.create(engine, checkfirst=True)
        # self.sql = sessionmaker(bind=engine)()

    def Build(self):
        self.appList = [
            ('/{0}/models'.format(self.srv_name), ModelProc, dict(sql=self.sql)),
            ('/{0}/models/(\w+)'.format(self.srv_name), ModelProcID, dict(sql=self.sql)),
            ('/{0}/models_exist/(\w+)'.format(self.srv_name), ModelExist, dict(sql=self.sql)),
            ('/{0}/property/(\w+)'.format(self.srv_name), Property, dict(srv=self.srv)),
            ('/{0}/action/(\w+)'.format(self.srv_name), Action, dict(srv=self.srv)),
            ('/{0}/event/(\w+)'.format(self.srv_name), Event, dict(srv=self.srv)),
            ('/{0}/mqtt/(\w+)'.format(self.srv_name), MqttOp, dict(srv=self.srv)),
            ('/{0}/devices'.format(self.srv_name), DevProc, dict(sql=self.sql, srv=self.srv)),
            ('/{0}/devices/(\w+)'.format(self.srv_name), DevProcID, dict(sql=self.sql, srv=self.srv)),
        ]
        self.httpApp = Application(self.appList)
        self.httpServer = HTTPServer(self.httpApp)
        self.httpServer.bind(self.config['PORT'])
        if 'HTTP_THREAD' in self.config:
            self.httpServer.start(self.config['HTTP_THREAD'])
        else:
            self.httpServer.start(1)

    def Run(self):
        IOLoop.current().start()

class ModelProc(CustomHandler):
    def initialize(self, sql):
        self.sql = sql
        
    # Add new model
    def post(self):
        print(self.request.headers['Content-Type'])
        model = self.sql.query(Entry).filter_by(id=self.get_argument('id')).first()

        if model == None:
            # Add
            model = Entry(id=self.get_argument('id'), content=self.get_argument('content'))
            print("Entry Added")
            self.sql.add(model)
        else:
            # Update
            model.content = self.get_argument('content')
            print("Entry exists, update")
        self.sql.commit()
        self.set_status(200)
        self.write('{0}'.format(model))

    # Get all models
    def get(self):
        print("Get Models")
        model = self.sql.query(Entry).all()
        self.set_status(200)
        self.write("{0}".format(model))

class ModelProcID(CustomHandler):
    def initialize(self, sql):
        self.sql = sql

    # Delete model
    def delete(self, id):
        print("Delete Entry - ID: "+ id)
        model = self.sql.query(Entry).filter_by(id=id).first()
        self.sql.delete(model)
        self.sql.commit()
        self.set_status(200)
        self.write("{0}".format(model))
                
    # Update model
    def post(self, id):
        print("Update Entry - ID: "+ id)
        model = self.sql.query(Entry).filter_by(id=id).first()
        model.content = self.get_argument('content')
        self.sql.commit()
        self.set_status(200)
        self.write("{0}".format(model))
        
    # Get model
    def get(self, id: str):
        print("Get Entry - ID: "+ id)
        model = self.sql.query(Entry).filter_by(id=id).first()
        self.set_status(200)
        self.write("{0}".format(model))

class ModelExist(CustomHandler):
    def initialize(self, sql):
        self.sql = sql

    # Check exist
    def get(self, id: str):
        model = self.sql.query(Entry).filter_by(id=id).first()
        self.set_status(200)
        if model == None:
            print("Entry Not Exist - ID: "+ id)
            self.write("false")
        else:
            print("Entry Exist - ID: "+ id)
            self.write("true")


# 读取/操作

# GET: {srv-name}/property/{property-name}
# POST: {srv-name}/action/{function-name}
# POST & MQTT: {srv-name}/event/{event-name}

class Property(CustomHandler):
    def initialize(self, srv):
        self.srv = srv

    def post(self, key: str):
        content = self.get_argument('content')
        is_read = self.get_argument('is_read')
        if is_read:
            self.write(json.dumps(self.srv.ReadProperty(key, content), ensure_ascii=False))
        else:
            self.write(json.dumps(self.srv.WriteProperty(key, content), ensure_ascii=False))

class Action(CustomHandler):
    def initialize(self, srv):
        self.srv = srv
        
    def get(self, func_name: str):
        self.write(json.dumps(self.srv.Execute(func_name), ensure_ascii=False))

    def post(self, func_name: str):
        content = self.get_argument('content')
        self.write(json.dumps(self.srv.Execute(func_name, content), ensure_ascii=False))

class Event(CustomHandler):
    def initialize(self, srv):
        self.srv = srv
        self.mqtt = srv.mqtt

    def post(self, event_name: str):
        setup = int(self.get_argument('setup')) # 0 = off, 1 = on
        pub_topic = self.get_argument('pub_topic')
        qos = 1
        try:
            qos = int(self.get_argument('qos'))
        except:
            pass

        print("Event Subscribed: {0}, {1}".format(setup, pub_topic))

        def on_event_callback(content):
            if (setup > 0):
                print("Event auto-pubed: {0}, {1}".format(setup, pub_topic))
                self.mqtt.publish(pub_topic, json.dumps({'content': content}, ensure_ascii=False), qos)

        if not hasattr(self.srv.app,'ecbs'):
            print("ecb not initiated")
            self.write("Error: ecb not initiated")
        else:
            self.srv.app.ecbs[event_name] = on_event_callback
            self.write("OK")

# MQTT 操作 (Flow)
class MqttOp(CustomHandler):
    def initialize(self, srv):
        self.srv = srv
        self.mqtt = srv.mqtt

    def post(self, func_name: str):
        op = self.get_argument('op')
        sub_topic = None
        
        try:
            sub_topic = self.get_argument('sub_topic')
        except:
            pass

        pub_topic = self.get_argument('pub_topic')
        qos = 1
        
        try:
            qos = int(self.get_argument('qos'))
        except:
            pass

        print("MQTT Op: {0}, {1}, {2}".format(op, sub_topic, pub_topic))

        # Automate: sub func input, pub func output
        if (op == "add"):
            if (sub_topic != None):
                self.mqtt.subscribe(sub_topic, qos)
            
            # Inject constants
            constants = {}
            try:
                constants = json.loads(self.get_argument('constants'))
            except:
                pass
    
            def on_subs_callback(client, userdata, msg):
                msg.payload = json.loads(msg.payload)
                msg.payload.update(constants)

                result = self.srv.Execute(func_name, msg.payload)
                if result is not None:
                    # Decode input
                    self.mqtt.publish(pub_topic, json.dumps({'content': self.srv.Execute(func_name, msg.payload)}, ensure_ascii=False), qos)
            # Sub input
            self.mqtt.message_callback_add(sub_topic, on_subs_callback)
        elif (op == "remove"):
            self.mqtt.unsubscribe(sub_topic)
            self.mqtt.message_callback_remove(sub_topic)
        self.write("OK")

# Protocol 协议服务专用
class DevProc(CustomHandler):
    def initialize(self, sql, srv):
        self.sql = sql
        self.srv = srv
        
    # Add new model
    def post(self):
        print(self.request.headers['Content-Type'])

        req = json.loads(self.request.body)
        req_json = json.dumps(req, ensure_ascii=False)
        id = req['id']

        model = self.sql.query(Entry).filter_by(id=id).first()

        if model == None:
            # Add
            model = Entry(id=id, content=req_json)
            print("Device Added")
            res = self.srv.AddDev(req)
            # if res is not None:
            #     self.write(str(res))
            #     return
            self.sql.add(model)
        else:
            # Update
            res = self.srv.UpdateDev(req)
            # if res is not None:
            #     self.write(str(res))
            #     return
            model.content = req_json
            print("Device exists, update")
        self.sql.commit()
        self.set_status(200)
        self.write('Device Added: {0}'.format(id))

    # Get all models
    def get(self):
        models = self.sql.query(Entry).all()
        for m in models:
            m.content = json.dumps(json.loads(m.content), ensure_ascii=False)
        models = json.dumps([{"id":m.id, "content":m.content} for m in models], ensure_ascii=False)
        self.set_status(200)
        self.write(models)

class DevProcID(CustomHandler):
    def initialize(self, sql, srv):
        self.sql = sql
        self.srv = srv

    # Delete model
    def delete(self, id):
        print("Delete Device - ID: "+ id)
        model = self.sql.query(Entry).filter_by(id=id).first()
        if model is None:
            self.write('Device does not exist - ID: ' + id)

        res = self.srv.DeleteDev(id)
        if res is not None:
            self.write(str(res))
            return
        self.sql.delete(model)
        self.sql.commit()
        self.set_status(200)
        self.write('Device Deleted: {0}'.format(id))
        
    # Get model
    def get(self, id: str):
        print("Get Device - ID: " + id)
        m = self.sql.query(Entry).filter_by(id=id).first()
        model = json.dumps({"id":m.id, "content":m.content}, ensure_ascii=False)
        self.set_status(200)
        self.write(model)
