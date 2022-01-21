"""TODO doc"""

import inspect
import os
import pkg_resources
import random
import sys
import time
import uuid
import logging
import threading
import logging
import json

from datetime import datetime
from pathlib import Path

from ejerico.sdk.annotations import singleton
from ejerico.sdk.config import ConfigManager
from ejerico.sdk.logging import LoggingManager

from ejerico.sdk.rdf.entity import Entity, Facility

__all__=["StatManager","Stat"]

@singleton
class StatManager(object):
    """TODO doc"""

    def __init__(self):
        self._config = ConfigManager.instance()
        self._logger = LoggingManager.instance().getLogger()
        self._stats = {}

        logpath = "{}{}.ejerico{}logs".format(Path.home(), os.sep, os.sep); 
        os.makedirs(logpath, exist_ok=True)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        logsize  = 4 * 1024 * 1024

        self._logger_entity = logging.getLogger("ejerico-harvesting-entity")
        handler_entity = logging.handlers.RotatingFileHandler("{}{}stats-entity.log".format(logpath, os.sep), maxBytes=logsize, backupCount=10)
        handler_entity.setLevel(logging.INFO)
        handler_entity.setFormatter(formatter)
        self._logger_entity.addHandler(handler_entity)
        #self._logger_entity.addHandler(logging.handlers.SysLogHandler())

        self._logger_entity_type = logging.getLogger("ejerico-harvesting-entity-type")
        handler_entity_type = logging.handlers.RotatingFileHandler("{}{}stats-entity-type.log".format(logpath, os.sep), maxBytes=logsize, backupCount=10)
        handler_entity_type.setLevel(logging.INFO)
        handler_entity_type.setFormatter(formatter)
        self._logger_entity_type.addHandler(handler_entity_type)
        #self._logger_entity_type.addHandler(logging.handlers.SysLogHandler())

        self._logger_harvest = logging.getLogger("ejerico-harvesting")
        handler_harvest = logging.handlers.RotatingFileHandler("{}{}stats-harvester.log".format(logpath, os.sep), maxBytes=logsize, backupCount=10)
        handler_harvest.setLevel(logging.INFO)
        handler_harvest.setFormatter(formatter)
        self._logger_harvest.addHandler(handler_harvest)
        #self._logger_harvest.addHandler(logging.handlers.SysLogHandler())

    def boot(self):
        #get stats/metrics url parameters from config
        pass

    def getStat(self, name=None):
        if name is None: name = self.__inferCallerID()
        if name not in self._stats: self._stats[name] = Stat(name)
        return self._stats[name]

    def releaseStat(self, name=None):
        if name is None:
            name = self.__inferCallerID()

        if name in self._stats:
            del self._stats[name]

    def __inferCallerID(self):
        callerID = None 
        try:
            caller = sys._getframe(2)
            caller_locals = caller.f_locals
            if "self" in caller_locals:
                caller_self = caller_locals["self"]
                callerID = callerID or (getattr(caller_self, "name") if hasattr(caller_self, "name") else callerID)
                callerID = callerID or (getattr(caller_self, "ID") if hasattr(caller_self, "ID") else callerID)
        except Exception as e: 
            logging.error(e)
        return uuid.uuid4() if callerID is None else callerID

class Stat(object):
    """TODO doc"""

    def __init__(self, ID):
        object.__init__(self)
        self._key_lock = threading.Lock()
        self._ID = ID
        self._source = ID
        self._harvesting_plugin = None
        self._harvesting_globalID = None
        self._harvesting_workerID = None
        self._harvesting_spanID = None
        self._harvesting_timestamp = None
        self._harvesting_plugin = None
        self._harvesting_items = 0
        self._harvesting_items_valid = 0
        self._harvesting_items_not_valid = 0
        self._harvesting_entities = {}

    def __getattr__(self, name):
        if  name not in self.__dict__: setattr(self, name, 0)
        return self.__dict__[name]

    @property
    def ID(self):
        return self._ID

    @property
    def source(self):
        return self._source

    @property
    def plugin(self):
        return self._harvesting_plugin

    @property
    def processed(self):
        return self._harvesting_items
    @processed.setter
    def processed(self, value):
        self._harvesting_items += value

    @property
    def processed_valid(self):
        return self._harvesting_items_valid
    @processed_valid.setter
    def processed_valid(self, value):
        self._harvesting_items_valid += value

    @property
    def processed_not_valid(self):
        return self._harvesting_items_not_valid
    @processed_not_valid.setter
    def processed_not_valid(self, value):
        self._harvesting_items_not_valid += value

    def clear(self):
        for key in self.__dict__:
            if key.startswith('_'): continue
            setattr(self, key, 0)

    def computeHarvester(self):
        self._key_lock.acquire(timeout=5)
        try:
            stats_harvest = {}
            for key in self.__dict__:
                if key.startswith('_'): continue
                stats_harvest[key.replace("__", ".")] = getattr(self, key)

            if 0 != len(stats_harvest):
                stats_harvest["guid"] = self._harvesting_globalID
                stats_harvest["wuid"] = self._harvesting_workerID
                stats_harvest["suid"] = self._harvesting_spanID
                stats_harvest["plugin"] = self._harvesting_plugin
                stats_harvest["htimestamp"] = datetime.fromtimestamp(self._harvesting_timestamp).strftime("%Y-%m-%dT%H:%M:%S")
                stats_harvest["timestamp"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                StatManager.instance()._logger_harvest.info(json.dumps(stats_harvest))
        except Exception as e: 
            logging.error("[Stat:computeHarvester] something was wrong computing 'Harvester' stats")
        self._key_lock.release()

    def computeEntity(self, entity):
        self._key_lock.acquire(timeout=5)
        try:
            if entity is not  None and isinstance(entity, Entity):
                kind = entity.strbase()

                ##[CASE] stats for harvester
                self._harvesting_items += 1
                self._harvesting_items_valid += (1 if entity.is_valid else 0)
                self._harvesting_items_not_valid += (0 if entity.is_valid else 1)

                self._source = entity.source if entity.source is not None else self._source
                
                if kind not in self._harvesting_entities: self._harvesting_entities[kind] = {}
                for key in entity.attributes():
                    value = getattr(entity, key)
                    if key not in self._harvesting_entities[kind]: self._harvesting_entities[kind][key] = 0
                    self._harvesting_entities[kind][key] += (len(value) if isinstance(value, list) else 1)

                entity_attributes = entity.attributes()
                for key in [k for k in self._harvesting_entities[kind] if not k.endswith("_missing")  and k not in entity_attributes]:
                    key = "{}_missing".format(key)
                    if key not in self._harvesting_entities[kind]: self._harvesting_entities[kind][key] = 0
                    self._harvesting_entities[kind][key] += 1

                if  0 == (self._harvesting_items%100): 
                    stats_entity_type = {}
                    stats_entity_type["guid"] = self._harvesting_globalID
                    stats_entity_type["wuid"] = self._harvesting_workerID
                    stats_entity_type["suid"] = self._harvesting_spanID
                    stats_entity_type["plugin"] = self._harvesting_plugin
                    stats_entity_type["htimestamp"] = datetime.fromtimestamp(self._harvesting_timestamp).strftime("%Y-%m-%dT%H:%M:%S")
                    stats_entity_type["timestamp"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                    stats_entity_type["items"] = self._harvesting_items
                    stats_entity_type["valids"] = self._harvesting_items_valid
                    stats_entity_type["not_valids"] = self._harvesting_items_not_valid
                    stats_entity_type["kind"] = kind
                    stats_entity_type["source"] = entity.source
                    stats_entity_type["attributes"] = {}
                    for key in self._harvesting_entities[kind]:
                        stats_entity_type["attributes"][key] = self._harvesting_entities[kind][key]
                    StatManager.instance()._logger_entity_type.info(json.dumps(stats_entity_type))

                ##[CASE] stats for entity
                stats_entity = {}
                stats_entity["guid"] = self._harvesting_globalID
                stats_entity["wuid"] = self._harvesting_workerID
                stats_entity["suid"] = self._harvesting_spanID
                stats_entity["plugin"] = self._harvesting_plugin
                stats_entity["htimestamp"] = datetime.fromtimestamp(self._harvesting_timestamp).strftime("%Y-%m-%dT%H:%M:%S")
                stats_entity["timestamp"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                stats_entity["valid"] = entity.is_valid
                stats_entity["kind"] = kind
                stats_entity["source"] = entity.source
                stats_entity["attributes"] = {k:0 for k in self._harvesting_entities[kind] if not k.endswith("_missing")}
                for key in stats_entity["attributes"]:
                    stats_entity["attributes"][key] += 1 if key in entity_attributes else 0
                StatManager.instance()._logger_entity.info(json.dumps(stats_entity))
        except Exception as e: 
            logging.error("[Stat:computeEntity] something was wrong computing 'Entity' stats")
        self._key_lock.release()

    

    