"""
TODO doc 
"""

import asyncio
import concurrent.futures
import datetime
import importlib
import inspect
import gc
import os
import pathlib
import pkg_resources
import random
import signal
import sys
import threading
import time
import uuid
import logging
import random
import profile

from ejerico.sdk.annotations import singleton
from ejerico.sdk.config import ConfigManager
from ejerico.sdk.logging import LoggingManager
from ejerico.sdk.stat import StatManager
from ejerico.sdk.rdf.graph_factory import GraphFactory
from ejerico.sdk.utils import format_exception
from ejerico.sdk.rdf.entity import EntityMapper

from ejerico.harvester_database import HarvesterDatabase
from ejerico.harvester_helper import HarvesterHelper
from ejerico.harvester_data import HarvesterData
from ejerico.harvester_config import HarvesterConfig
from ejerico.harvester_extension import HarvesterExtension

__all__ = ["HarvesteringExecutor", "Harvester"]

class HarvesteringExecutor(object):

    def __init__(self): 
        """TODO doc"""

        logging.info("[HarvesteringExecutor::__init__] entering method")
        self._shared_data = {}
        self._harvesters = None
        self._graph = GraphFactory.createGraph()

        self._config = ConfigManager.instance()
        self._stat = StatManager.instance()
        self._logging = LoggingManager.instance()
        self._logger = self._logging.getLogger()
        
        self._id = self._config.get("id", default="jerico-wp7.5")
        self._timeout = self._config.get("timeout", default=0)
        self._run_once = self._config.get("run_once", default=True)
        self._workers = self._config.get("workers", default=0)
        self._interlaced = self._config.get("interlaced_mode", default=False)
        self._force_update = self._config.get("force_update", default=False)
        self._name = self._config.get("name")
        self._namespace = self._config.get("namespace", default="ejerico")

        self._key_lock = threading.Lock()

        self._plugins = {}
        for entry_point in pkg_resources.iter_entry_points("ejerico.plugins.harvester"):
            self._plugins[entry_point.name.replace("Harvester","").lower()] = entry_point.load()
        for entry_point in pkg_resources.iter_entry_points("socib.plugins.harvester"):
            self._plugins[entry_point.name.replace("Harvester","").lower()] = entry_point.load()
        for entry_point in pkg_resources.iter_entry_points("{}.plugins.harvester".format(self._namespace)):
            self._plugins[entry_point.name.replace("Harvester","").lower()] = entry_point.load()

        self._plugin_names = [key for key in self._plugins.keys()]
        self._done = False

        source_path = "{}/.ejerico/extensions".format(str(pathlib.Path.home()))
        if os.path.exists(source_path): sys.path.append(source_path)
        
        for source_path in self._config.get("source_path", default=[]):
            if os.path.exists(source_path): sys.path.append(source_path)

        if self._workers:
            self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=self._workers)

    async def __arun__(self):
        logging.info("[HarvesteringExecutor::__arun__] entering method")

        loop = asyncio.get_running_loop() 

        for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGABRT):
            loop.add_signal_handler(sig, self.__handler__, sig)

        while not self._done:
        
            #get list of harvester from config
            workers = []
            for h in self._config.get("harvesters", default=[]):
                h = h.strip().lower(); p=None
                w = h
                ws = [
                    w,
                    w.replace('_', ''),
                    "harvester_{}".format(w) if not w.startswith("harvester_") else w,
                    ("harvester_{}".format(w)).replace('_', '') if not w.startswith("harvester_") else w,
                ]
                
                for w in ws:
                    if w in self._plugin_names: 
                        n = w if h == w else h
                        p = w
                    elif self._config.get("plugin", namespace=w):
                        n = w
                        p = self._config.get("plugin", namespace=w)
                else:
                    if p is None:
                        logging.critical("[HarvesteringExecutor::__arun__] error unknown harvester ({})".format(h.strip().lower()))
                        raise SystemExit

                for _ in (range(self._config.get("workers", namespace="harvester_{}".format(w), default=1))):       
                    workers.append((w,p,h))

            if not workers: 
                logging.info("[HarvesteringExecutor::__arun__] empty harvester list")
                sys.exit(0)
            else:
                for i in range(5): random.shuffle(workers)
            
            #run harvesters
            current_timestamp = int(datetime.datetime.now().timestamp())

            self._harvesters = []
            for w in workers:
                if w[1] not in self._plugins:
                    logging.error("[HarvesteringExecutor::__arun__] is plugin '{}' installed in system?".format(w[1]))
                    sys.exit(1)

                harvester_class = self._plugins[w[1]]
                harvester_class._config = HarvesterConfig(self._config, w[2] if w[2].startswith("harvester_") else "harvester_{}".format(w[2]))
                harvester_class._logger = self._logger
                harvester_class._harvesting_timestamp = current_timestamp
                harvester_class._harvesting_id = str(uuid.uuid4())
                harvester_class._mapper = EntityMapper.instance()
                harvester_class._home = "{}{}.ejerico".format(str(pathlib.Path.home()), os.sep)

                harvester_class._executor = self
                harvester_class._delegated_requests = []
                
                if not hasattr(harvester_class, "_mapping_file"):
                    mapping_file = self._getHarvesterMappingFile(harvester_class)
                    if os.path.exists(mapping_file): harvester_class._mapper.load_mapping_definition(mapping_file)
                    
                    mapping_file = "harvester_{}_mapping.json".format(w[2])
                    mapping_file = self._config.get("mapping_file", namespace="harvester_{}".format(w[2]), default=mapping_file)
                    mapping_file = "{}{}".format(self._getConfigPath(), mapping_file)
                    if os.path.exists(mapping_file): harvester_class._mapper.load_mapping_definition(mapping_file)
                    harvester_class._mapping_file = mapping_file

                if not hasattr(harvester_class, "_cls_extension"):
                    source_extension = self._config.get("source_extension", namespace="harvester_{}".format(w[2]))
                    if source_extension is not None:
                        try:
                            source_extension = source_extension.split(':')
                            source_modules = source_extension[0] if 2 == len(source_extension) else []
                            mod = importlib.import_module(source_modules)
                            my_cls_extension = getattr(mod, source_extension[1])
                            if issubclass(my_cls_extension, HarvesterExtension): harvester_class._cls_extension = my_cls_extension
                        except (ModuleNotFoundError, AttributeError) as e:
                            logging.info("[HarvesteringExecutor::__arun__] error importing module '{}'".format(source_extension[0]))
                            sys.exit(0)

                harvesterID = str(uuid.uuid4())  
                harvester = harvester_class()
                harvester._id = "{}-{}".format(self._id , harvesterID)
                harvester._name = self._config.get("name", namespace="harvester_{}".format(w[2]), default=harvester_class.__name__)
                harvester._delegator = []
                harvester._stat =  self._stat.getStat(harvester._id)#(harvester._name)
                harvester._stat._harvesting_plugin = harvester_class.__name__
                harvester._stat._harvesting_globalID = harvester_class._harvesting_id
                harvester._stat._harvesting_workerID = harvesterID
                harvester._stat._harvesting_timestamp = harvester_class._harvesting_timestamp

                harvester._namespace = self._namespace if self._namespace else n
                harvester._namespace = self._config.get("namespace", namespace="harvester_{}".format(w[2]), default=harvester._namespace)
                if harvester._name is None:
                    harvester._name = harvester_class.__name__
                    if w[0] != w[1]:
                        harvester._name = ''.join(x for x in w[0].replace('_',' ').replace('-', ' ').title() if not x.isspace())
                        harvester._name = "{}Harvester".format(harvester._name.upper())
                #harvester._name = harvester._name.lower()  
                harvester._idx = sum(harvester._name == h._name for h in self._harvesters)
                
                if harvester._name not in self._shared_data: self._shared_data[harvester._name] = HarvesterData()
                harvester._shared_data = self._shared_data[harvester._name]
    
                harvester._timeout = self._config.get("timeout", namespace="harvester_{}".format(w[2]), default=0)
                harvester._max_errors = self._config.get("max_errors", namespace="harvester_{}".format(w[2]), default=10)
                harvester._errors = 0
                harvester._iteration = 0
                harvester._done = False
                harvester._zombie = True #race condition 
                harvester.helper.graph = harvester.graph

                if hasattr(harvester, "_cls_extension"): 
                    harvester._extension = harvester._cls_extension()
                    harvester._extension.name = harvester._name
                    harvester._extension.namespace = harvester._namespace
                    harvester._extension.helper = harvester.helper
                    harvester._extension.graph = GraphFactory.createGraph()

                harvester._timeout = harvester.config.get("timeout", default=self._interlaced)
                harvester._run_once = harvester.config.get("run_once", default=self._run_once)
                harvester._workers = harvester.config.get("workers", default=self._workers)
                harvester._interlaced = harvester.config.get("interlaced_mode", default=self._interlaced)
                harvester._force_update = harvester.config.get("force_update", default=self._force_update)

                self._harvesters.append(harvester)

            for i in range(random.randint(3,9)): random.shuffle(self._harvesters)
            #for harvesters - setup
            for p in list(set([w[1] for w in workers])):
                self._plugins[p].setup()

            iteration_time = time.time()

            if self._workers:
                tasks = [loop.run_in_executor(self._executor, harvester.__run__) for harvester in self._harvesters]
                
                pending = len(tasks)
                while pending: 
                    completed, pending = await asyncio.wait(tasks)
                    logging.info("[HarvesteringExecutor::__arun__] completed: {} pending: {}".format(len(completed), pending))
            else:
                tasks = [asyncio.create_task(harvester.__arun__()) for harvester in self._harvesters]
                    
                #wait until all harvester instances are finished
                no_running_tasks = 1
                while 0 < no_running_tasks:
                    no_running_tasks = 0 

                    await asyncio.sleep(1)
                    current_task = asyncio.current_task(loop=loop)   
                    
                    tasks = asyncio.all_tasks(loop=loop)
                    for task in tasks:
                        if current_task is not task: 
                            no_running_tasks += (0 if task.cancelled() or task.done() else 1)
                    
                    #logging.info("[HarvesteringExecutor::__arun__] running tasks: {}".format(no_running_tasks))

            iteration_time = time.time() - iteration_time 
            if iteration_time < self._timeout: await asyncio.sleep(int(self._timeout-iteration_time))

            #for harvesters - release
            for p in list(set([w[1] for w in workers])):
                self._plugins[p]._executor = None
                self._plugins[p]._config = None
                self._plugins[p]._logger = None
                self._plugins[p]._stat =  None
                self._plugins[p].release()

            del self._harvesters
            self._shared_data.clear()

            self._clearObsoleteGraphResources(current_timestamp)
            
            gc.collect()

            self._done = True if self._run_once else self._done

        current_task = asyncio.current_task(loop=loop)   
        tasks = asyncio.all_tasks(loop=loop)
        for task in tasks:
            if current_task is not task and not task.cancelled and not task.done(): task.cancel()

        logging.info("[HarvesteringExecutor::__arun__] exitting method")
    
    def __handler__(self, sig):
        logging.info("[HarvesteringExecutor::__handler__] entering method with signal: {}".format(sig))

        self._done = True

        loop = asyncio.get_running_loop()

        for task in asyncio.all_tasks(loop=loop): task.cancel()

        loop.remove_signal_handler(signal.SIGTERM)
        loop.add_signal_handler(signal.SIGINT, lambda: None)
        loop.add_signal_handler(signal.SIGABRT, lambda: None)

        logging.info("[HarvesteringExecutor::__arun__] exitting method")

    def _clearObsoleteGraphResources(self, current_timestamp):
        logging.info("[HarvesteringExecutor::_clearObsoleteGraphResources] entering method")
        logging.info("[HarvesteringExecutor::_clearObsoleteGraphResources] todo purge graph tiplets before {}".format(datetime.datetime.fromtimestamp(current_timestamp)))

    def _getConfigPath(self):
        paths = None
        if sys.platform == "linux" or sys.platform == "linux2":
            paths = ("{}/.ejerico/harvester.ini".format(str(pathlib.Path.home())),"/etc/ejerico/harvester.ini")
        elif sys.platform == "darwin":
            paths = ("{}/.ejerico/harvester.ini".format(str(pathlib.Path.home())),"/etc/ejerico/harvester.ini")
        elif sys.platform == "win32":
            pass
        
        for path in paths:
             if os.path.exists(path): 
                 return path.replace("harvester.ini", "")
             
        return None

    def _getHarvesterMappingFile(self,harvester_class):
        mapfile = inspect.getfile(harvester_class)
        mapfile = mapfile.split(os.sep)
        mapfile = mapfile[:-1]
        mapfile.append("data")
        mapfile.append("default_entity_mapping.json")
        mapfile = os.sep.join(mapfile)
        return mapfile

    def run(self):
        """ TODO doc"""
         
        logging.info("[HarvesteringExecutor::run] entering method with PID: {}".format(os.getpid()))
        try:
            asyncio.run(self.__arun__())
        except asyncio.CancelledError as e:
            logging.info("[HarvesteringExecutor::run] exception 'CancelledError' caught in event loop")
        except KeyboardInterrupt as e: 
            logging.info("[HarvesteringExecutor::run] exception 'KeyboardInterrupt' caught in event loop")
        logging.info("[HarvesteringExecutor::run] exitting method")

    def delegate_request(self, uri=None, from_harvester=None):
        logging.info("[HarvesteringExecutor::run] entering method")
        if uri is None or from_harvester is None: return
    
        self._key_lock.acquire(timeout=5)
        try:
            for p_name, p_class in self._plugins.items():
                if p_class == from_harvester.__class__: continue
                if hasattr(p_class, "can_harvest_delegated_request"):
                    rst = getattr(p_class, "can_harvest_delegated_request")(uri)
                    if rst:
                        for h in self._harvesters: 
                            if h.__class__ == p_class.__class__: p_class._delegated_requests.append(uri); return

                        p_class._config = from_harvester.__class__._config
                        p_class._logger = from_harvester.__class__._logger
                        p_class._harvesting_timestamp = from_harvester.__class__._harvesting_timestamp
                        p_class._harvesting_id = from_harvester.__class__._harvesting_id
                        p_class._mapper = from_harvester.__class__._mapper
                        p_class._home = from_harvester.__class__._home
                        p_class._executor = from_harvester.__class__._executor
                        p_class._mapping_file = from_harvester.__class__._mapping_file

                        if p_class.__name__ not in self._shared_data: self._shared_data[p_class.__name__] = HarvesterData()

                        if not hasattr(p_class, "_delegated_requests"): setattr(p_class, "_delegated_requests", [])
                        p_class._delegated_requests.append(uri)
                        
                        for h in self._harvesters:
                            if h.__class__ == from_harvester.__class__:
                                p_instance = p_class()
                                p_instance._id = from_harvester._id
                                p_instance._name = "({}){}".format(p_class.__name__,from_harvester._name)
                                p_instance._stat = from_harvester._stat
                                p_instance._namespace = from_harvester._namespace
                                p_instance._idx = from_harvester._idx
                                p_instance._shared_data = self._shared_data[p_class.__name__]
                                p_instance._timeout = from_harvester._timeout
                                p_instance._max_errors = from_harvester._max_errors
                                p_instance._errors = from_harvester._errors
                                p_instance._iteration = from_harvester._iteration
                                p_instance._done = from_harvester._done
                                p_instance._zombie = from_harvester._zombie
                                p_instance.helper.graph = from_harvester._graph
                                p_instance._delegator = []
                                p_instance.pre_harvest()
                                h._delegator.append(p_instance)
        except Exception as e: 
            logging.error("[HarvesteringExecutor::delegate_request] error executing method ({})".format(e))
        finally:    
            self._key_lock.release()

class Harvester(object): 
    """ TODO doc """

    _key_lock = threading.Lock()

    def __init__(self):
        object.__init__(self) 
        logging.info("[Harvester::__init__] entering method")

    def __del__(self): 
        logging.info("[Harvester::__del__] entering method")
        if "_graph_" in self.__dict__:
            self._graph.close(commit_pending_transaction=True)  

    def __run__(self):
        #logging.info("[Harvester::__run__] entering method") 

        self._errors = 0
        self._iteration = 0
        self._zombie = False

        while not self.groupDone: #self._done:
            iteration_time = time.time()
            try:
                self.pre_harvest()
                self.__run_delegator__(method="pre_harvest")

                if self._interlaced: time.sleep(0) 
                self.do_harvest()
                self.__run_delegator__(method="do_harvest")

                if self._interlaced: time.sleep(0)
                self.post_harvest()
                self.__run_delegator__(method="post_harvest")  

                if self._interlaced: time.sleep(0)
                self.stats.computeHarvester()
                self._errors = 0
                self._iteration += 1
                
            except Exception as e:
                self._errors += 1 if self._errors < self._max_errors else 0
                logging.error(format_exception(e))
                logging.error("[Harvester::__run__] TODO report error ({}/{})".format(self._errors, self._max_errors)) 
                if self._errors == self._max_errors: self.__groupDone(True)

            if iteration_time < self._timeout:
                time.sleep(int(self._timeout-iteration_time))

        #else: logging.info("[Harvester::__run__] exitting of working loop")
        #logging.info("[Harvester::__run__] exitting method")

    def __run_delegator__(self, delegated_from=None, method=None):
        if self._interlaced: time.sleep(0) 
        delegated_from = self if delegated_from is None else delegated_from
        for delegated_to in delegated_from._delegator: 
            getattr(delegated_to, method)()
            self.__run_delegator__(delegated_from=delegated_to, method=method)

    async def __arun__(self):
        #logging.info("[Harvester::__arun__] entering method") 

        self._iteration = 0
        self._zombie = False

        while not self._done:
            iteration_time = time.time()
            try:
                await self.__pre_harvest__()
                await asyncio.sleep(1)
                self._iteration += 1
            except Exception as e:
                self._errors += 1 if self._errors < self._max_errors else 0
                logging.error(format_exception(e))
                logging.error("[Harvester::__run__] TODO report error ({}/{})".format(self._errors, self._max_errors))
                if self._errors == self._max_errors: self._done = True 

            iteration_time = time.time() - iteration_time 

            if iteration_time < self._timeout:
                await asyncio.sleep(int(self._timeout-iteration_time))
        #else: logging.info("[Harvester::__arun__] exitting of working loop")
        #logging.info("[Harvester::__arun__] exitting method")

    async def __arun_delegator__(self, delegated_from=None, method=None):
        if self._interlaced: await asyncio.sleep(1) 
        delegated_from = self if delegated_from is None else delegated_from
        for delegated_to in delegated_from._delegator: 
            getattr(delegated_to, method)() 
            self.__arun_delegator__(delegated_from=delegated_to, method=method)

    async def __pre_harvest__(self):
        """TODO doc"""
        if self._interlaced: await asyncio.sleep(1) 
        self.pre_harvest()
        await self.__arun_delegator__(method="pre_harvest")
        if self._interlaced: await asyncio.sleep(1)
        await self.__do_harvest__()

    async def __do_harvest__(self): 
        """TODO doc""" 
        if self._interlaced: await asyncio.sleep(1) 
        self.do_harvest()
        await self.__arun_delegator__(method="do_harvest")
        if self._interlaced: await asyncio.sleep(1)
        await self.__post_harvest__()

    async def __post_harvest__(self): 
        """TODO doc"""
        if self._interlaced: await asyncio.sleep(1)  
        self.post_harvest()
        await self.__arun_delegator__(method="post_harvest")
        if self._interlaced: await asyncio.sleep(1)
        self.stats.computeHarvester()
    
    @staticmethod
    def setup():
        """TODO doc"""
        logging.info("[Harvester::setup] entering method")

    @staticmethod
    def release():
        """TODO doc"""
        logging.info("[Harvester::release] entering method")

    def pre_harvest(self):
        """TODO doc""" 
        logging.info("[Harvester::pre_harvest] entering method")

    def do_harvest(self): 
        """TODO doc""" 
        logging.info("[Harvester::do_harvest] entering method (iteration: {})".format(self.iteration))

    def post_harvest(self): 
        """TODO doc""" 
        logging.info("[Harvester::post_harvest] entering method")

    @property
    def executor(self):
        return self._executor
    @property
    def delegator(self):
        return self._delegator
        
    @property
    def delegated_requests(self):
        return self._delegated_requests
        
    @property
    def ID(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def namespace(self):
        return self._namespace

    @property
    def index(self):
        return self._idx

    @property
    def force_update(self):
        return self._force_update

    @property
    def graph(self):
        if "_graph" not in self.__dict__: self._graph = GraphFactory.createGraph()
        return self._graph

    @property
    def db(self):
        if "_db" not in self.__dict__: self._db = HarvesterDatabase.instance()
        return self._db

    @property
    def config(self):
        return self._config

    @property
    def logger(self):
        return self._logger

    @property
    def stats(self):
        return self._stat

    @property
    def shared_data(self):
        return self._shared_data

    @property
    def mapper(self):
        return self._mapper

    @property
    def home(self):
        return self._home

    @property
    def extension(self):
        return self._extension if hasattr(self, "_extension") else None
    
    @property
    def iteration(self):
        return self._iteration

    @property
    def harvesting_timestamp(self):
        return self._harvesting_timestamp

    @property
    def harvestID(self):
        return self._harvesting_id

    @property
    def done(self):
        return False if self._done is None else self._done
    @done.setter
    def done(self, value):
        self._done = value
        
    @property 
    def groupDone(self):
        Harvester._key_lock.acquire()
        all_done = True
        for brother in self.brothers:
            all_done = all_done and (brother.done or brother._zombie)
        Harvester._key_lock.release()
        return all_done
    def __groupDone(self, value):
        Harvester._key_lock.acquire()
        for brother in self.brothers:
            brother.done = value
        Harvester._key_lock.release() 
    
    @property
    def helper(self):
        if "_helper" not in self.__dict__: self._helper = HarvesterHelper()
        return self._helper

    @property
    def brothers(self):
        return [h for h in self._executor._harvesters if h._name == self._name]

    @property 
    def activeBrothers(self):
        rst = []
        Harvester._key_lock.acquire() 
        for brother in self.brothers:
            if not(brother.done or brother._zombie): rst.append(brother)
        Harvester._key_lock.release()
        return rst

