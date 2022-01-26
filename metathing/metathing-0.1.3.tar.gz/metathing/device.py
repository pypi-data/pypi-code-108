#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# 增/删/改/查/获取所有

# POST: {srv-name}/models
# DELETE: {srv-name}/models/{instID}
# POST: {srv-name}/models/{instID}
# GET: {srv-name}/models/{instID}
# GET: {srv-name}/models

from .sql import Entry, Flow
from tornado.web import Application,RequestHandler
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
import json
from pdb import set_trace as stop

from tornado.escape import json_decode

class CustomHandler(RequestHandler):
    def get_argument(self, id:str):
        if self.request.headers['Content-Type'] == 'application/json':
            args = json_decode(self.request.body)
            return args[id]
        return super(CustomHandler, self).get_argument(id)

    def get_argument_dict(self):
        params = self.request.arguments
        for k,v in params.items():
            params[k] = v[0].decode("utf-8")
        return params

# Base for protocol service
class Device():
    # def __init__(self, config: dict, srv_name: str, model) -> None:
    def __init__(self, srv, model) -> None:
        self.config = srv.config
        self.srv_name = srv.srv_name
        if isinstance(model, str):
            self.model = json.loads(model)
        else:
            self.model = model

        self.srv = srv
        self.sql = srv.sql
        self.mqtt = srv.mqtt
        if 'id' in model:
            self.dev_id = model['id']
            self.build()
        
        self.dev_srvs = {}
        if 'services' in model:
            for s in model['services']:
                self.dev_srvs[s['id']] = s

    def initialize(self):
        raise NotImplementedError

    def build(self):
        self.appList = [
            ('/{0}/devices/{1}/ping'.format(self.srv_name, self.dev_id), Ping),
            ('/{0}/devices/{1}/resources/(\w+)'.format(self.srv_name, self.dev_id), DevProperty, dict(dev=self, srv=self.srv)),
            ('/{0}/devices/{1}/services/(\w+)'.format(self.srv_name, self.dev_id), DevService, dict(dev=self, srv=self.srv)),
            ('/{0}/devices/{1}/events/(\w+)'.format(self.srv_name, self.dev_id), DevEvent, dict(dev=self, srv=self.srv)),
            ('/{0}/devices/{1}/selectors/(\w+)'.format(self.srv_name, self.dev_id), DevSelector, dict(dev=self, srv=self.srv)),
            ('/{0}/devices/{1}/mqtt/(\w+)'.format(self.srv_name, self.dev_id), DevMqttOp, dict(dev=self, srv=self.srv)),
        ]

        self.srv.http.httpApp.add_handlers(r".*", self.appList)

    # Selector
    def selector(self, func_name:str, content = None):
        # print("selector function: " + func_name)
        if (content == None or content == {}):
            return getattr(self, func_name)()
        else:
            if isinstance(content, str):
                return getattr(self, func_name)(**(json.loads(content)))
            elif isinstance(content, dict):
                return getattr(self, func_name)(**content)
            else:
                return "Content type is not supported"

    def service(self, srv_name: str, content = None):
        if self.dev_srvs is None:
            return "Device has no service"
        if srv_name in self.dev_srvs:
            srv_model = self.dev_srvs[srv_name]
            func_name = srv_model['selector']
            return self.selector(func_name, content)
        else:
            return "Device does not have service: %s" % srv_name

    def flow(self, op:str, srv_name='', sub_topic:str=None, pub_topic:str=None, qos=1 ):
        qos = int(qos)
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
                msg.payload = json.loads(json.loads(msg.payload)["content"])
                msg.payload.update(constants)

                result = self.service(srv_name, msg.payload)
                if result is not None:
                    # Decode input
                    self.mqtt.publish(pub_topic, json.dumps({'content': result}, ensure_ascii=False), qos)

            self.mqtt.message_callback_add(sub_topic, on_subs_callback)
            # Sub input
            print("MQTT Service Subscribe: {0}, {1}, {2}, Added service: {3}".format(op, sub_topic, pub_topic, srv_name))

            # Save
            flow_models_JSON = self.srv.sql.query(Flow).filter_by(id=self.model['id']).first()
            flow_model = {"dev_id": self.model['id'],"srv_name": srv_name,"sub_topic": sub_topic,"pub_topic": pub_topic, "qos": qos}

            if flow_models_JSON is None:
                flow_models = [flow_model]
            else:
                flow_models = json.loads(flow_models_JSON.content)
                if flow_model in flow_models:
                    return
                else:
                    flow_models.append(flow_model)

            if flow_models_JSON is None:
                self.sql.add(Flow(id=self.model['id'], content=json.dumps(flow_models)))
            else:
                flow_models_JSON.content = json.dumps(flow_models)
            self.sql.commit()
            print("Flow Added")

        elif (op == "remove"):
            print("MQTT Service Unsubscribe")
            flow_models_JSON = self.srv.sql.query(Flow).filter_by(id=self.model['id']).first()
            if flow_models_JSON is not None:
                flow_models = json.loads(flow_models_JSON.content)
                for model in flow_models:
                    if sub_topic == model['sub_topic']:
                        self.mqtt.unsubscribe(model['sub_topic'])
                        self.mqtt.message_callback_remove(model['sub_topic'])
                        flow_models.remove(model)
                        print("Flow Deleted: " + model['sub_topic'])
                flow_models_JSON.content = json.dumps(flow_models)
            self.sql.commit()

class Ping(CustomHandler):
    def get(self):
        self.write("OK")

# # 读取/操作

# # GET: {srv-name}/property/{property-name}
# # POST: {srv-name}/action/{function-name}
# # POST & MQTT: {srv-name}/event/{event-name}

class DevProperty(CustomHandler):
    def initialize(self, dev, srv):
        self.dev = dev
        self.srv = srv

    def post(self, key: str):
        content = self.get_argument('content')
        is_read = self.get_argument('is_read')
        if is_read:
            self.write(json.dumps(self.srv.ReadProperty(key, content)))
        else:
            self.write(json.dumps(self.srv.WriteProperty(key, content)))

class DevService(CustomHandler):
    def initialize(self, dev, srv):
        self.dev = dev
        self.srv = srv
        
    def get(self, srv_name: str):
        self.write(json.dumps(self.srv.selector(func_name)))

    def post(self, srv_name: str):
        args = self.get_argument_dict()
        self.write(json.dumps(self.dev.service(srv_name, args)))

class DevSelector(CustomHandler):
    def initialize(self, dev, srv):
        self.dev = dev
        self.srv = srv
        self.mqtt = srv.mqtt

    def post(self, func_name: str):
        args = self.get_argument_dict()
        self.write(json.dumps(self.dev.selector(func_name, args)))

class DevEvent(CustomHandler):
    def initialize(self, dev, srv):
        self.dev = dev
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
class DevMqttOp(CustomHandler):
    def initialize(self, dev, srv):
        self.dev = dev
        self.srv = srv
        self.mqtt = srv.mqtt

    def post(self, srv_name: str):
        self.dev.flow(srv_name=srv_name, **json_decode(self.request.body))

        # op = self.get_argument('op')
        # sub_topic = None
        
        # try:
        #     sub_topic = self.get_argument('sub_topic')
        # except:
        #     pass

        # pub_topic = self.get_argument('pub_topic')
        # qos = 1
        
        # try:
        #     qos = int(self.get_argument('qos'))
        # except:
        #     pass

        # # Automate: sub func input, pub func output
        # if (op == "add"):
        #     if (sub_topic != None):
        #         self.mqtt.subscribe(sub_topic, qos)
            
        #     # Inject constants
        #     constants = {}
        #     try:
        #         constants = json.loads(self.get_argument('constants'))
        #     except:
        #         pass
    
        #     def on_subs_callback(client, userdata, msg):
        #         msg.payload = json.loads(json.loads(msg.payload)["content"])
        #         msg.payload.update(constants)

        #         result = self.dev.service(srv_name, msg.payload)
        #         if result is not None:
        #             # Decode input
        #             self.mqtt.publish(pub_topic, json.dumps({'content': result}, ensure_ascii=False), qos)

        #     # Sub input
        #     print("MQTT Service Subscribe: {0}, {1}, {2}, Added service: {3}".format(op, sub_topic, pub_topic, srv_name))

        #     # Save
        #     stop()
        #     dev_id = self.dev.model['id']
        #     flow_models_JSON = self.srv.sql.query(Flow).filter_by(id=dev_id).first()

        #     flow_model = json.dumps()
        #     flow_id = sub_topic

        #     if flow_model is None:
        #         flow_models = []
        #     else:
        #         flow_models = json.loads(flow_models_JSON)

        #     model = Entry(id=id, content=req_json)
        #     print("Device Added")
        #     res = self.srv.AddDev(req)
        #     if res is not None:
        #         self.write(str(res))
        #         return
        #     self.sql.add(model)

        #     if model == None:
        #         # Add
        #         model = Entry(id=id, content=req_json)
        #         print("Device Added")
        #         res = self.srv.AddDev(req)
        #         if res is not None:
        #             self.write(str(res))
        #             return
        #         self.sql.add(model)
        #     else:
        #         # Update
        #         res = self.srv.UpdateDev(req)
        #         if res is not None:
        #             self.write(str(res))
        #             return
        #         model.content = req_json
        #         print("Device exists, update")

        #     self.mqtt.message_callback_add(sub_topic, on_subs_callback)
        # elif (op == "remove"):
        #     print("MQTT Service Unsubscribe: {0}".format(sub_topic))
        #     self.mqtt.unsubscribe(sub_topic)
        #     self.mqtt.message_callback_remove(sub_topic)
        self.write("OK")

# # Protocol 协议服务专用
# class DevProc(CustomHandler):
#     def initialize(self, dev, srv):
#         self.dev = dev
#         self.srv = srv
        
#     # Add new model
#     def post(self):
#         print(self.request.headers['Content-Type'])
#         model = self.sql.query(Entry).filter_by(id=self.get_argument('id')).first()

#         if model == None:
#             # Add
#             model = Entry(id=self.get_argument('id'), content=self.request.body.decode("utf-8"))
#             print("Device Added")
#             self.sql.add(model)
#         else:
#             # Update
#             model.content = self.request.body.decode("utf-8")
#             print("Device exists, update")
#         self.sql.commit()
#         self.set_status(200)
#         self.write('{0}'.format(model))

#     # Get all models
#     def get(self):
#         print("Get Devices")
#         model = self.sql.query(Entry).all()
#         # stop()
#         # model = [c.content for c in self.sql.query(Entry).all()]
#         self.set_status(200)
#         self.write("{0}".format(model))

# class DevProcID(CustomHandler):
#     def initialize(self, dev, srv):
#         self.dev = dev
#         self.srv = srv

#     # Delete model
#     def delete(self, id):
#         print("Delete Device - ID: "+ id)
#         model = self.sql.query(Entry).filter_by(id=id).first()
#         self.sql.delete(model)
#         self.sql.commit()
#         self.set_status(200)
#         self.write("{0}".format(model))
                
#     # Update model
#     def post(self, id):
#         print("Update Device - ID: "+ id)
#         model = self.sql.query(Entry).filter_by(id=id).first()
#         model.content = self.request.body.decode("utf-8")
#         self.sql.commit()
#         self.set_status(200)
#         self.write("{0}".format(model))
        
#     # Get model
#     def get(self, id: str):
#         print("Get Entry - ID: "+ id)
#         model = self.sql.query(Entry).filter_by(id=id).first()
#         self.set_status(200)
#         self.write("{0}".format(model))