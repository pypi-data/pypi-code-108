#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import functools
import sys, os
from .context_start import AutoStartContext
from lcyframe.libs import utils


class ServicesFindet(object):
    """
    Global ContextManage Register module
    """

    def __init__(self, app=None, model=None):
        self.app = app or type("app", (object,), {})
        self.model = model or type("model", (object,), {})

    def __call__(self, c):
        for f in dir(self):
            if f.startswith("import_"):
                r = getattr(self, f)(c)
                if r:
                    logging.debug("conntcion to %s success." % f.split("_")[-1])

    def import_mongo(self, config):
        f = config.get("mongo_config", {})
        if f:
            AutoStartContext.start_mongodb(f)
            from .singleton import MongoCon
            from .permissions import Permission
            self.__mount_attribute("mongo", MongoCon.get_database(**f))

            Permission.mongo = MongoCon.get_database(**f)
            self.__mount_attribute("Permission", Permission.initial())
            return True

    def import_mysql(self, config):
        f = config.get("mysql_config", {})
        if f:
            from .singleton import PyMysqlCon
            self.__mount_attribute("mysql", PyMysqlCon.get_connection(**f))
            return True

    def import_redis(self, config):
        f = config.get("redis_config")
        if f:
            AutoStartContext.start_redis(f)
            from .singleton import RedisCon
            self.__mount_attribute("redis", RedisCon.get_connection(**f))
            return True

    def import_ssdb(self, config):
        f = config.get("ssdb_config")
        if f:
            AutoStartContext.start_ssdb(f)
            from .singleton import SSDBCon
            self.__mount_attribute("ssdb", SSDBCon.get_connection(**f))
            return True

    def import_mq(self, config):
        f = config.get("mq_config")
        if f:
            from .singleton import MQCon
            self.__mount_attribute("mq", MQCon.get_connection(**f))
            return True

    def import_nsq(self, config):
        f = config.get("nsq_config")
        if f:
            from .singleton import NsqCon
            nsq = NsqCon.get_connection(**f)
            self.__mount_attribute("nsq", nsq)

            p = utils.fix_path(os.path.join(config["ROOT"], "producer/nsq"))
            if os.path.exists(p) and not f.get("producer_dir"):
                config["nsq_config"]["producer_dir"] = ["producer/nsq"]

            if f.get("producer_dir"):
                self._import_nsq_producer(nsq, config["ROOT"], config["nsq_config"]["producer_dir"])

            return nsq

    def import_mqtt(self, config):
        f = config.get("mqtt_config")
        if f and f.get("run", True):
            from .singleton import MqttCon
            mqtt = MqttCon.get_connection(**f)
            self.__mount_attribute("mqtt", mqtt)

            p = utils.fix_path(os.path.join(config["ROOT"], "producer/mqtt"))
            if os.path.exists(p) and not f.get("producer_dir"):
                config["mqtt_config"]["producer_dir"] = ["producer/mqtt"]

            if f.get("producer_dir"):
                self._import_mqtt_producer(mqtt, config["ROOT"], config["mqtt_config"]["producer_dir"])

            return mqtt

    def import_celery(self, config):
        f = config.get("celery_config")
        if f and f.get("run", True):
            from .singleton import CeleryCon
            from lcyframe.libs.celery_route import Events

            celeryconfig = f["config_dir"]
            if not celeryconfig.endswith(".py"):
                celeryconfig = celeryconfig.replace(".", "/")
                celeryconfig += ".py"
            if not os.path.exists(utils.fix_path(os.path.join(config["ROOT"], celeryconfig))):
                raise Exception("file does not exist：%s" % celeryconfig)
            celeryconfig = celeryconfig.rstrip(".py")
            celeryconfig = celeryconfig.lstrip("/")
            celeryconfig = celeryconfig.replace("/", ".")
            os.environ['CELERY_CONFIG_MODULE'] = celeryconfig

            p = utils.fix_path(os.path.join(config["ROOT"], "works/celery"))
            if os.path.exists(p) and not f.get("workers_dir"):
                config["celery_config"]["workers_dir"] = ["works/celery"]

            app = CeleryCon.get_connection(**f)
            self._import_celery_worker(app, config["ROOT"], config["celery_config"]["workers_dir"], Events)
            self.__mount_attribute("celery", app)
            return app

    def import_beanstalk(self, config):
        f = config.get("beanstalk_config")
        if not f:
            return
        from .singleton import BeanstalkCon
        from lcyframe.libs.beanstalk_route import Events

        p = utils.fix_path(os.path.join(config["ROOT"], "works/beanstalk"))
        if os.path.exists(p) and not f.get("workers_dir"):
            f["workers_dir"] = ["works/beanstalk"]

        app = BeanstalkCon.get_connection(**f)
        setattr(Events, "beanstalk", app)
        self._import_beanstalk_worker(app, config["ROOT"], f["workers_dir"], Events)
        self.__mount_attribute("beanstalk", app)
        return app

    def import_mob(self, config):
        f = config.get("mob_config")
        if f:
            from .singleton import MobCon
            self.__mount_attribute("mob", MobCon.get_connection(**f))
            return True

    def import_qiniu(self, config):
        f = config.get("qiniu_config")
        if f:
            from .singleton import QinNiuCon
            self.__mount_attribute("qiniu", QinNiuCon.get_connection(**f))
            return True

    def import_emchat(self, config):
        f = config.get("emchat_config")
        if f:
            from .singleton import EmchatCon
            self.__mount_attribute("emchat", EmchatCon.get_connection(**f))
            return True

    def import_token(self, config):
        tc = config["token_config"]
        if "secret" not in tc:
            raise Exception("you must give token secret in you setting.yml")
        self.__mount_attribute("token_config", tc)
        self.__mount_attribute("Token", self._get_jwt(tc))
        return True

    def import_aes(self, config):
        tc = config.get("aes_config", {})
        from .aes import AES
        self.__mount_attribute("aes", AES(tc.get("secret")))
        return True

    def import_graylog(self, config):
        c = config.get("graylog_config")
        if c:
            from .singleton import GrayLogCon
            self.__mount_attribute("graylog", GrayLogCon(**c))
            return True

    def import_errors(self, config):
        return
        model_name = self.fix_module_path(config["errors_dir"]) + "." + "errors.py".rstrip(".py")
        objs = __import__(model_name, fromlist=["*"])
        ApiError = type("ApiError", (object,), {})
        import inspect
        for p in dir(objs):
            if p.startswith("__"):
                continue
            if not inspect.isclass(getattr(objs, p)):
                continue
            if not issubclass(getattr(objs, p), BaseException):
                continue

            setattr(ApiError, p, getattr(objs, p))
        self.__mount_attribute("ApiError", ApiError)

    def __mount_attribute(self, model_name, value):
        if self.app:
            setattr(self.app, model_name, value)
        if self.model:
            setattr(self.model, model_name, value)

    def _get_jwt(self, config):
        """

        :param p:
        :return:
        """

        return functools.partial(self._token, config["secret"], config["expire"])

    def _token(self, secret, expire, uid):
        from .JWT import JwtToken
        return JwtToken(uid, secret, int(expire))

    def _import_nsq_producer(self, app, root_path, produce_path):
        """
        register nsq producer
        :return:
        """
        # for dir in config["nsq_config"]["producer_dir"]:
        #     root_path = os.path.join(config["ROOT"], dir)
        #     new_path = os.path.join(root_path, "__init__.py")
        #     if os.path.exists(new_path):
        #         os.remove(new_path)
        #     if os.path.exists(os.path.join(root_path, "__init__.pyc")):
        #         os.remove(os.path.join(root_path, "__init__.pyc"))
        #
        #     with open(new_path, 'w+', encoding='utf-8') as f:
        #         f.write(pytemplate.get_nsq_producer_init(root_path, dir))
        #
        #     sys.path.append(root_path)
        #     m = ".".join(root_path.split("/")[-2:])
        #     import_module(m)

        for work in produce_path:
            for root, dirs, files in os.walk(os.path.join(root_path, work)):
                for file in files:
                    if file.startswith("__"):
                        continue

                    if file.endswith(".pyc"):
                        continue

                    if not file.endswith(".py"):
                        continue
                    model_name = self.fix_module_path(root.replace(root_path, "")) + "." + file.rstrip(".py")
                    objs = __import__(model_name, fromlist=["*"])

                    for p in dir(objs):
                        if p.startswith("__"):
                            continue

                        # if not p.lower().startswith("publish"):
                        # logging.debug("nsq producer [%s] load fail. it must been start with 'publish'" % p)
                        #    continue

                        if not hasattr(getattr(objs, p), "topic"):
                            continue

                        logging.debug("nsq producer [%s] register success!" % p)
                        setattr(app, p, getattr(objs, p)())

    def _import_mqtt_producer(self, app, root_path, produce_path):
        """
        register mqtt producer
        :return:
        """
        # for dir in config["mqtt_config"]["producer_dir"]:
        #     root_path = os.path.join(config["ROOT"], dir)
        #     new_path = os.path.join(root_path, "__init__.py")
        #     if os.path.exists(new_path):
        #         os.remove(new_path)
        #     if os.path.exists(os.path.join(root_path, "__init__.pyc")):
        #         os.remove(os.path.join(root_path, "__init__.pyc"))
        #
        #     with open(new_path, 'w+', encoding='utf-8') as f:
        #         f.write(yaml2py.get_mqtt_producer_init(root_path, dir))
        #
        #     sys.path.append(root_path)
        #     m = ".".join(root_path.split("/")[-2:])
        #     import_module(m)

        for work in produce_path:
            for root, dirs, files in os.walk(utils.fix_path(os.path.join(root_path, work))):
                for file in files:
                    if file.startswith("__"):
                        continue

                    if file.endswith(".pyc"):
                        continue

                    if not file.endswith(".py"):
                        continue
                    model_name = self.fix_module_path(root.replace(root_path, "")) + "." + file.rstrip(".py")
                    objs = __import__(model_name, fromlist=["*"])

                    for p in dir(objs):
                        if p.startswith("__"):
                            continue

                        # if not p.lower().startswith("publish"):
                        # logging.debug("mqtt producer [%s] load fail. it must been start with 'publish'" % p)
                        #    continue

                        if not hasattr(getattr(objs, p), "topic"):
                            continue

                        logging.debug("mqtt producer [%s] register success!" % p)
                        setattr(app, p, getattr(objs, p)())

    def _import_celery_worker(self, app, root_path, workers_dir, Events):
        """
        register celery tasks
        :return:
        """
        # for dir in config["celery_config"]["workers_dir"]:
        #     root_path = os.path.join(config["ROOT"], dir)
        #     new_path = os.path.join(root_path, "__init__.py")
        #     # if os.path.exists(new_path):
        #     #     os.remove(new_path)
        #     if os.path.exists(os.path.join(root_path, "__init__.pyc")):
        #         os.remove(os.path.join(root_path, "__init__.pyc"))
        #
        #     with open(new_path, 'w+', encoding='utf-8') as f:
        #         f.write(yaml2py.get_celery_works_init(root_path, dir))
        #
        #     sys.path.append(root_path)
        #     m = ".".join(root_path.split("/")[-2:])
        #     import_module(m)

        for work in workers_dir:
            for root, dirs, files in os.walk(utils.fix_path(os.path.join(root_path, work))):
                for file in files:
                    if file.startswith("__"):
                        continue

                    if file.endswith(".pyc"):
                        continue

                    if not file.endswith(".py"):
                        continue

                    model_name = self.fix_module_path(root.replace(root_path, "")) + "." + file.rstrip(".py")
                    objs = __import__(model_name, fromlist=["*"])
                    setattr(Events, objs.__name__.split(".")[-1], objs)

                    for p in dir(objs):
                        if p.startswith("__"):
                            continue

                        if type(getattr(objs, p)) == type:
                            if not hasattr(getattr(objs, p), "queue"):
                                continue

                            if hasattr(app, p) and p != 'BaseEvent':
                                raise Exception("exists same attribute：%s" % p)

                        logging.debug("celery task [%s] register success!" % p)
                        setattr(Events, p, getattr(objs, p))

                    setattr(app, Events.__name__, Events)
        return app

    def _import_beanstalk_worker(self, app, root_path, workers_dir, Events):
        """
        register celery tasks
        :return:
        """
        from lcyframe.libs.beanstalk_route import BsRoute
        workers = BsRoute.get_workers(root_path, workers_dir)
        for class_name, objs in workers.items():
            if not hasattr(objs, "tube"):
                continue
            setattr(app, class_name, type(class_name, (Events,), {"tube": objs.tube, "classname": objs.__name__})())
            logging.debug("beanstalk task class [%s] register success!" % class_name)
        app.workers = workers
        return app

    def fix_module_path(self, module_path):
        module_path = utils.fix_path(module_path)
        module_path = module_path.lstrip("/").replace("/", ".").replace("//", ".").replace("/", ".")
        return module_path

    def add_service(self, service_name, service_obj):
        """
        external a service into app and model, only
        :param service_name:
        :param service_obj:
        :return:

        :Make your service and register it before starting
        :example::
            s = ServicesFindet

            def import_mq(self, config):
                f = config["mq_config"]
                from .singleton import MQCon
                mq = MQCon.get_connection(**f)
                return mq

            # 1、app_start:
                s.add_service("mq", import_mq(config))

                app = App(**config)
                app.start()

            # 2、mq_start:
                s.add_service("mq", import_mq(config))

                w = MqttWorker(**config)
                s(w, BaseModel)(config)
                w.start()

            # 3、or, anywhere do it
                from lcyframe.base import BaseHandler, BaseModel
                BaseHandler.mq = import_mq(**f)
                BaseModel.mq = import_mq(**f)

            # Now you can use it like this::
                self.mq ...
                self.model.mq ...
        """

        if service_obj is None:
            raise ValueError("An not None object must be returned in your service_obj()")

        if self.app is None:
            from lcyframe.base import BaseHandler
            self.app = BaseHandler
        if self.model is None:
            from lcyframe.base import BaseModel
            self.model = BaseModel

        setattr(self.app, service_name, service_obj)
        setattr(self.model, service_name, service_obj)

