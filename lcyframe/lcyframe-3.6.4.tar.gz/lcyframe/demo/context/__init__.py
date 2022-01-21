#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys, os
root_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(root_dir)
import platform
import logging
from tornado.options import options, define
from lcyframe.libs import yaml2py, utils
from lcyframe.libs.context_start import AutoStartContext
from lcyframe.libs.singleton import MongoCon
from model.schema.igGenerator_schema import IdGeneratorSchema
from model.igGenerator_model import IdGeneratorModel
# from model.schema.admin_schema import AdminSchema

class InitContext(object):
    config = None
    port = config_file = None

    @classmethod
    def get_context(cls, config_name=None):
        if not config_name:
            logging.warning("platform >>>>>>>>>>>:" + platform.node())
            if len(sys.argv) > 1:
                for item in sys.argv[1:]:
                    arg = item.lstrip("-").lstrip("--")
                    if "=" in arg:
                        name, equals, value = arg.partition("=")
                    else:
                        value = arg

                    if value.isdigit():
                        cls.port = int(value)
                        continue
                    if ".yml" in value:
                        cls.config_file = value
                        continue

                if not cls.config_file:
                    raise Exception("please run like this：python app.py --config=example.yml")

                sys.argv = sys.argv[0]
            else:
                if platform.node() in ["Online"]:
                    cls.config_file = "server_config.yml"
                elif platform.node() in ["app"]:
                    cls.config_file = "test_config.yml"
                elif platform.node() in ["vm"]:
                    cls.config_file = "vm_config.yml"
                elif platform.node() in ["Mac", "lcyMac.local"]:
                    cls.config_file = "localhost.yml"
                else:
                    cls.config_file = "example.yml"
        else:
            cls.config_file = config_name

        logging.warning(cls.config_file)
        cls.config = yaml2py.load_confog(os.path.join(os.path.dirname(__file__), cls.config_file))
        if cls.port:
            cls.config["wsgi"]["port"] = int(cls.port)
        cls.config["config_name"] = cls.config_file.split("/")[-1]
        cls.config["ROOT"] = utils.fix_path(os.path.dirname(os.path.dirname(__file__)))
        os.environ.app_config = cls.config
        return cls.config

    @classmethod
    def init_db(cls):
        AutoStartContext.start_mongodb(cls.config["mongo_config"])


        db = MongoCon().get_database(**cls.config["mongo_config"])
        if not db.id_generator.find().count():
            doc = vars(IdGeneratorSchema())
            doc["uid"] = 10000
            db[IdGeneratorSchema.collection].insert(doc)

        if not db.admin.find().count():

            docs = vars(AdminSchema())
            docs["uid"] = 10000
            docs["nick_name"] = "nick_name"
            docs["pass_word"] = utils.gen_salt_pwd("123456", docs["salt"])
            docs["gid"] = 1
            db[AdminSchema.collection].insert(docs)
