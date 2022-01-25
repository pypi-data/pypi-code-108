# -*- coding: future_fstrings -*-
import signal
import time
import traceback
from abc import ABCMeta, abstractmethod
import sys
import os
from concurrent import futures
from random import shuffle

import six
import datetime

from sumoappclient.common.ctocstatus import SourceHealthStatus
from sumoappclient.common.errors import InValidConfigException, FetchConfigException, ErrorType, AuthException, StoreException, SendDataException
from sumoappclient.common.logger import get_logger
from sumoappclient.common.utils import get_current_timestamp, compatibleabstractproperty, read_yaml_file
from sumoappclient.provider.factory import ProviderFactory
import pkg_resources
import psutil

def getProcessSize():
    processId = os.getpid()
    process = psutil.Process(processId)
    processMemorySizeInMB = process.memory_info().rss / (1024 * 1024)
    msgStr = f'''Process name: {process}, ProcessId: {processId}, RSS Memory (MB): {processMemorySizeInMB}'''
    return msgStr

@six.add_metaclass(ABCMeta)
class BaseOutputHandler(object):

    def __init__(self, config, *args, **kwargs):
        self.log = get_logger(__name__, **config['Logging'])
        self.setUp(config, *args, **kwargs)

    @abstractmethod
    def setUp(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def send(self, data):
        raise NotImplementedError()


    @classmethod
    def utf8len(cls, s):
        if not isinstance(s, bytes):
            s = s.encode('utf-8')

        length = len(s)
        del s
        return length

    def add_records(self, records, **kwargs):
        data = [record.get_log() for record in records]
        status = self.send(data, **kwargs)
        del data
        return True, status

    def flush_records(self, records=None, **kwargs):
        if records:
            data = [record.get_log() for record in records]
            status = self.send(data, **kwargs)
            del data
            return status
        return True


class ExecutionState(object):
    POLLING = "POLLING"
    STOP = "STOP_POLLING"
    BACKOFF = "BACKOFF"


@six.add_metaclass(ABCMeta)
class BaseCollector(object):

    COLLECTOR_PROCESS_NAME = ""

    def __init__(self, PROJECT_DIR):
        self.initialize(PROJECT_DIR)

    def initialize(self, PROJECT_DIR):
        # temporary logger for sending health status
        log = get_logger("tmp", force_create=True, ENABLE_LOGFILE=False, LOG_LEVEL="DEBUG")
        log.info(f'''Starting {self.COLLECTOR_PROCESS_NAME} Forwarder ...''',
                 extra={"status": SourceHealthStatus.StatusStarting})
        cfgpath = sys.argv[1] if len(sys.argv) > 1 else ''
        self.execution_state = ExecutionState.POLLING  # even in non c2c case this variable is used
        # 10 secs this duration is different than polling interval and is smaller
        period = 10
        # maxBackoff is the maximum number of period times to wait for before expiring expo backoff
        max_back_off_secs = 90 * 60 # 90 min
        base = 2
        self.is_first_fetch = True
        while True:
            try:
                environment = self.get_environment(PROJECT_DIR, self.CONFIG_FILENAME)
                op_cli = ProviderFactory.get_provider(environment)

                # Get config
                config_instance = op_cli.get_config("config", filename=self.CONFIG_FILENAME, root_dir=PROJECT_DIR, cfgpath=cfgpath)
                self.config = config_instance.get_config()
                self.log = get_logger(__name__, force_create=True, pkg_name=self.COLLECTOR_PROCESS_NAME, **self.config['Logging'])
                self.collection_config = self.config['Collection']

                self.kvstore = op_cli.get_storage("keyvalue", logger=self.log, name=self.collection_config['DBNAME'],
                                                  db_dir=self.collection_config.get("DB_DIR"))
                self.is_another_instance_running = not self.get_running_instance_lock()

                break
            except (AuthException, InValidConfigException) as e:
                # error handling for api threads
                # Here exc info is true because these are invalid config errors and are non recoverable
                log.error(f'''Initialize failed: {e}''', extra={"status": SourceHealthStatus.StatusError,
                                                         "errorCode": e.error_code,
                                                         "errorType": ErrorType.ERROR_CONFIG}, exc_info=True)
                raise e
            except (StoreException, FetchConfigException) as e:

                log.error(f'''Initialize failed: {e}''', extra={"status": SourceHealthStatus.StatusError,
                                                         "errorCode": e.error_code,
                                                         "errorType": ErrorType.ERROR_FRAMEWORK})

            except Exception as e:  # this includes FetchExceptionn
                # Here exc info is true because these are third party API errors and could be recoverable
                log.error(f'''Initialize failed: {e}''', extra={"status": SourceHealthStatus.StatusError,
                                                         "errorType": ErrorType.ERROR_GENERIC}, exc_info=True)

            duration = base * period
            if duration > max_back_off_secs:
                err_msg = f'''Initialized failed: MAX_BACKOFF_MINUTES limit reached {base}'''
                log.error(err_msg, extra={"status": SourceHealthStatus.StatusError, "errorType": ErrorType.ERROR_GENERIC})
                raise Exception(err_msg)
            else:
                log.debug(f'''Initialize: sleeping for {duration} secs, base {base}''')
                time.sleep(duration)
            base = base << 1

        signal.signal(signal.SIGINT, self.exit_gracefully)  # for Ctrl-C
        signal.signal(signal.SIGTERM, self.exit_gracefully)  # kill command
        self.num_workers = self.collection_config.get('NUM_WORKERS', 1)
        # initializing after validating config and fetching current state (assuming these are done in constructor of BaseAPI concrete implementations)
        self.log.info("Initialization completed", extra={"status": SourceHealthStatus.StatusInitialized})

    @compatibleabstractproperty
    def CONFIG_FILENAME(self):
        raise NotImplementedError()


    @compatibleabstractproperty
    def SINGLE_PROCESS_LOCK_KEY(self):
        raise NotImplementedError()

    @abstractmethod
    def build_task_params(self, *args, **kwargs):
        raise NotImplementedError()

    def run(self):
        has_any_error = False
        if not self.is_another_instance_running:
            task_params = []
            try:
                # initialising state
                task_params = self.build_task_params()
                # done so that same task is not produced always picked since num workers could be less than tasks
                if self.collection_config.get("IS_SHUFFLE_TASKS", True):
                    self.log.debug(f'''shuffling {len(task_params)} tasks''')
                    shuffle(task_params)
                all_futures = {}
                current_num_workers = min(self.num_workers, len(task_params))
                self.log.debug(f"spawning {current_num_workers} workers {getProcessSize()} for {self.COLLECTOR_PROCESS_NAME}")
                with futures.ThreadPoolExecutor(max_workers=current_num_workers) as executor:
                    results = {executor.submit(apiobj.fetch): apiobj for apiobj in task_params}
                    all_futures.update(results)
                    del results

                for future in futures.as_completed(all_futures):
                    param = all_futures[future]
                    api_type = str(param)
                    try:
                        future.result()
                    except (AuthException, InValidConfigException) as e:
                        # error handling for api threads
                        # Here exc info is true because these are invalid config errors and are non recoverable
                        self.log.error(f'''Thread: {api_type} {repr(e)}''', extra={"status": SourceHealthStatus.StatusError,
                                                                             "errorCode": e.error_code,
                                                                             "errorType": ErrorType.ERROR_CONFIG},
                                       exc_info=True)
                        self.execution_state = ExecutionState.STOP
                    except (StoreException, SendDataException) as e:

                        self.log.error(f'''Thread: {api_type} {repr(e)}''', extra={"status": SourceHealthStatus.StatusError,
                                                                             "errorCode": e.error_code,
                                                                             "errorType": ErrorType.ERROR_FRAMEWORK})
                        has_any_error = True
                    except Exception as e: # this includes FetchExceptionn
                        # Here exc info is true because these are third party API errors and could be recoverable
                        self.log.error(f'''Thread: {api_type} {repr(e)}''', extra={"status": SourceHealthStatus.StatusError,
                                                                             "errorType": ErrorType.ERROR_GENERIC},
                                       exc_info=True)
                        has_any_error = True
                    else:
                        if self.is_first_fetch:
                            self.log.info(f"Authentication successful for {self.COLLECTOR_PROCESS_NAME}", extra={"status": SourceHealthStatus.StatusAuthenticated})
                            self.is_first_fetch = False
                        self.log.info(f"Thread: {api_type} completed successfully for {self.COLLECTOR_PROCESS_NAME}")
                    del future
                del all_futures

            except Exception as e:

                self.log.error(f'''{repr(e)}''', extra={"status": SourceHealthStatus.StatusError,
                                                  "errorType": ErrorType.ERROR_GENERIC}, exc_info=True)
                has_any_error = True
            finally:
                # Cleaning up individual api objects - any sessions/connections
                for apiobj in task_params:
                    apiobj.close()
                    del apiobj
                del task_params
            if self.execution_state != ExecutionState.STOP:
                if has_any_error:
                    self.execution_state = ExecutionState.BACKOFF
                else:
                    self.execution_state = ExecutionState.POLLING
                    # collecting state will be set in healthstatushandler based on laststatus.
                    # Also if any one of the tasks fails then the status would be Error
                    self.log.info(f"All Threads completed successfully {getProcessSize()} for {self.COLLECTOR_PROCESS_NAME}", extra={"status": SourceHealthStatus.StatusCollecting})
            self.stop_running()
        else:
            if not self.is_process_running([self.COLLECTOR_PROCESS_NAME]):
                self.kvstore.release_lock_on_expired_key(self.SINGLE_PROCESS_LOCK_KEY)

    def execute(self):
        if self.collection_config["ENVIRONMENT"] == "ctoc":
            # function is invoked at periodic interval of polling interval secs

            polling_interval_secs = self.collection_config["POLLING_INTERVAL_MINUTES"] * 60
            # maxBackoff is the maximum number of period times to wait for before expiring expo backoff
            max_back_off_secs = self.collection_config["MAX_BACKOFF_MINUTES"] * 60
            base = 2
            sleep_time = polling_interval_secs
            self.execution_state = ExecutionState.POLLING
            while self.execution_state != ExecutionState.STOP:
                calling_time = time.time()
                self.run()
                execution_time = time.time() - calling_time

                if self.execution_state == ExecutionState.BACKOFF:
                    # below check is for integrations like SFDC which have a polling_interval_sec > 1hr
                    # to avoid small number of retries for large polling interval 10min minimum condition is applied
                    sleep_time = base * min(10 * 60, polling_interval_secs)
                    if sleep_time > max_back_off_secs:
                        self.execution_state = ExecutionState.STOP
                        err_msg = f'''Max backoff limit reached execution_state: {self.execution_state} backoff: {base} last_execution_time: {execution_time} sleep_time: {sleep_time - execution_time}'''
                        self.log.error(err_msg, extra={"status": SourceHealthStatus.StatusError,
                                                       "errorType": ErrorType.ERROR_GENERIC})
                        break
                    else:
                        base = base << 1

                elif self.execution_state == ExecutionState.POLLING:
                    # resetting to normal state
                    base = 2
                    sleep_time = polling_interval_secs

                self.log.info(f'''execution_state: {self.execution_state} backoff: {base} last_execution_time: {execution_time} sleep_time: {sleep_time - execution_time} memory: {getProcessSize()}''')
                if sleep_time - execution_time > 0:
                    # subtracting execution time so that run is invoked periodically like cron job
                    time.sleep(sleep_time - execution_time)
        else:
            # normal case it assumes there is some trigger which periodically triggers the script
            try:
                self.run()
            except BaseException as e:
                traceback.print_exc()

    def is_process_running(self, cmd_names):
        if not isinstance(cmd_names, list):
            cmd_names = [cmd_names]

        is_process_running = False
        if self.collection_config['ENVIRONMENT'] == "onprem":
            import psutil
            current_pid = os.getpid()
            for procobj in psutil.process_iter(attrs=['cmdline', 'pid']):
                cmds = procobj.info['cmdline']
                process_id = procobj.info['pid']
                if cmds:
                    cmdline = " ".join(cmds)
                    if any([cmd_name in cmdline and process_id != current_pid for cmd_name in cmd_names]):
                        self.log.info("running cmd line: %s process_id: %s current_pid: %s" % (
                                cmdline, process_id, current_pid))
                        is_process_running = True
                        break
        return is_process_running

    def name(self):
        return self.config['DeployMetaData']['PACKAGENAME']

    def version(self):
        try:
            return pkg_resources.get_distribution(self.config['DeployMetaData']['PACKAGENAME']).version
        except Exception:
            return ""

    def exit_gracefully(self, signum, frame):
        # this exits current thread
        if not self.is_another_instance_running:
            self.stop_running() # release lock if any
        self.kvstore.close()
        sys.exit(0)

    def get_running_instance_lock(self):
        self.log.debug("Acquiring single instance lock")
        return self.kvstore.acquire_lock(self.SINGLE_PROCESS_LOCK_KEY)

    def stop_running(self):
        self.log.debug("Releasing single instance lock")
        return self.kvstore.release_lock(self.SINGLE_PROCESS_LOCK_KEY)

    @staticmethod
    def get_environment(root_dir, config_filename):
        # getting and validating the config
        base_config_path = os.path.join(root_dir, config_filename)
        base_config = read_yaml_file(base_config_path)
        if ("Collection" in base_config and "ENVIRONMENT" in base_config["Collection"]) or os.getenv("ENVIRONMENT"):
            return os.getenv("ENVIRONMENT") if os.getenv("ENVIRONMENT") else base_config['Collection']['ENVIRONMENT']
        else:
            raise InValidConfigException("ENVIRONMENT is empty in configuration")


@six.add_metaclass(ABCMeta)
class BaseAPI(object):
    # Todo pagination/auth/

    def __init__(self, kvstore, config):
        self.kvstore = kvstore
        self.config = config
        self.start_time = datetime.datetime.utcnow()
        self.sumo_config = config['SumoLogic']
        self.collection_config = self.config['Collection']
        self.STOP_TIME_OFFSET_SECONDS = self.collection_config['TIMEOUT']
        self.DEFAULT_START_TIME_EPOCH = get_current_timestamp() - self.collection_config['BACKFILL_DAYS']*24*60*60
        self.log = get_logger(__name__, **self.config['Logging'])
        signal.signal(signal.SIGINT, self.exit_gracefully)  # for Ctrl-C
        signal.signal(signal.SIGTERM, self.exit_gracefully)  # kill command

    def get_function_timeout(self):
        timeout_config = {
            "onprem": float("Inf"),
            "aws": 15*60,
            "gcp": 5*60,
            "azure": 5*60,
            "ctoc": float("Inf")
        }
        return timeout_config[self.collection_config['ENVIRONMENT']]

    def is_time_remaining(self):
        now = datetime.datetime.utcnow()
        time_passed = (now - self.start_time).total_seconds()
        self.log.debug("checking time_passed: %s" % time_passed)
        has_time = time_passed + self.STOP_TIME_OFFSET_SECONDS < self.get_function_timeout()
        if not has_time:
            self.log.info("Shutting down not enough time")
        return has_time

    def __str__(self):
        return self.get_key()

    @abstractmethod
    def get_key(self):
        raise NotImplementedError()

    @abstractmethod
    def save_state(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def get_state(self):
        raise NotImplementedError()

    @abstractmethod
    def build_fetch_params(self):
        raise NotImplementedError()

    @abstractmethod
    def build_send_params(self):
        raise NotImplementedError()

    @abstractmethod
    def transform_data(self, content):
        raise NotImplementedError()

    @abstractmethod
    def fetch(self):
        raise NotImplementedError()

    def exit_gracefully(self, signum, frame):
        self.log.info("Exiting Gracefully killed by SignalNum: %s" % signum)
        self.save_state()
        self.close()
        # this exits current thread
        sys.exit(0)

    def get_updated_state(self, data, current_state):
        raise NotImplementedError()

    def set_initial_state(self):
        raise NotImplementedError()

    def close(self):
        pass

@six.add_metaclass(ABCMeta)
class BaseRecord(object):

    def __init__(self, config, raw_msg, *args, **kwargs):
        self.config = config
        self.log = get_logger(__name__, **self.config['Logging'])
        self.collection_config = self.config['Collection']
        self.raw_msg = raw_msg

    def to_raw(self):
        return self.raw_msg

    @abstractmethod
    def to_cnc(self):
        raise NotImplementedError()

    @abstractmethod
    def to_siem(self):
        raise NotImplementedError()

    def get_log(self):
        if self.collection_config['ENVIRONMENT'] == "ctoc":

            if self.config["SumoLogic"].get("systemConfig", {}).get("fields",{}).get("_siemForward", False):
                return self.to_siem()

            return self.to_cnc()
        else:
            return self.to_raw()


