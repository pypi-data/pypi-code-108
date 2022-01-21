"""
Apache Mesos Provider to scheduler Apache Airflow DAG's under Mesos.
"""
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from queue import Queue
from typing import Any, Dict, Optional
from threading import Thread

import threading
import json
import urllib3
import ast


from avmesos.client import MesosClient

from airflow.configuration import conf
from airflow.exceptions import AirflowException
from airflow.executors.base_executor import BaseExecutor, CommandType
from airflow.models.taskinstance import TaskInstanceKey
from airflow.utils.session import provide_session
from airflow.utils.state import State
from flask import Flask, request, Response
from waitress import serve

FRAMEWORK_CONNID_PREFIX = "mesos_framework_"

urllib3.disable_warnings()

app = Flask(__name__)


def get_framework_name():
    """Get the mesos framework name if its set in airflow.cfg"""
    return conf.get("mesos", "FRAMEWORK_NAME")


# pylint: disable=too-many-nested-blocks
# pylint: disable=too-many-instance-attributes
class AirflowMesosScheduler(MesosClient):
    """
    Airflow Mesos scheduler implements mesos scheduler interface
    to schedule airflow tasks on mesos
    Basically, it schedules a command like
    'airflow run <dag_id> <task_instance_id> <start_date> --local -p=<pickle>'
    to run on a mesos slave
    """

    # pylint: disable=super-init-not-called
    def __init__(
        self, executor, task_queue, result_queue, task_cpu: int = 1, task_mem: int = 256
    ):
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.task_cpu = task_cpu
        self.task_mem = task_mem
        self.task_counter = 0
        self.task_key_map: Dict[str, str] = {}
        self.log = executor.log
        self.client = executor.client
        self.executor = executor
        self.driver = None
        self.tasks: Dict[str, str] = {}

        if not conf.get("mesos", "DOCKER_IMAGE_SLAVE"):
            self.log.error("Expecting docker image for  mesos executor")
            raise AirflowException(
                "mesos.slave_docker_image not provided for mesos executor"
            )

        self.mesos_slave_docker_image = conf.get("mesos", "DOCKER_IMAGE_SLAVE")
        self.mesos_docker_volume_driver = conf.get("mesos", "DOCKER_VOLUME_DRIVER")
        self.mesos_docker_volume_dag_name = conf.get("mesos", "DOCKER_VOLUME_DAG_NAME")
        self.mesos_docker_environment = conf.get("mesos", "DOCKER_ENVIRONMENT", fallback="")
        self.mesos_docker_volume_dag_container_path = conf.get(
            "mesos", "DOCKER_VOLUME_DAG_CONTAINER_PATH"
        )
        self.mesos_docker_volume_logs_name = conf.get(
            "mesos", "DOCKER_VOLUME_LOGS_NAME"
        )
        self.mesos_docker_volume_logs_container_path = conf.get(
            "mesos", "DOCKER_VOLUME_LOGS_CONTAINER_PATH"
        )
        self.mesos_docker_sock = conf.get("mesos", "DOCKER_SOCK")
        self.core_sql_alchemy_conn = conf.get("core", "SQL_ALCHEMY_CONN")
        self.core_fernet_key = conf.get("core", "FERNET_KEY")
        self.logging_logging_level = conf.get("logging", "LOGGING_LEVEL")
        self.command_shell = str(
            conf.get("mesos", "COMMAND_SHELL", fallback=True)
        ).lower()

    def resource_heartbeat(self, heartbeat):
        """If we got a heartbeat, run checks"""
        self.log.info("Heartbeat")
        if self.task_queue.empty():
            self.log.debug("Suppress Mesos Framework")
            self.driver.suppress()
        else:
            self.log.debug("Revive Mesos Framework")
            self.driver.revive()
       
    def resource_offers(self, offers):
        """If we got a offer, run a queued task"""
        if (not self.task_queue.empty()):
            for i, offer in enumerate(offers):
                if not self.run_job(offer):
                     offertmp = offer.get_offer()
                     self.log.info("Declined Offer: %s", offertmp["id"]["value"])
                     offer.decline()        

    # pylint: disable=too-many-branches
    def run_job(self, mesos_offer):
        """Start a queued Airflow task in Mesos"""
        offer = mesos_offer.get_offer()
        tasks = []
        option = {}
        offer_cpus = 0
        offer_mem = 0
        force_pull = "true"
        container_type = "DOCKER"
        cpu = self.task_cpu
        mem = self.task_mem
        image = self.mesos_slave_docker_image
        airflow_task_id = None

        for resource in offer["resources"]:
            if resource["name"] == "cpus":
                offer_cpus = resource["scalar"]["value"]
                self.log.info("CPU's %d", offer_cpus)
            elif resource["name"] == "mem":
                offer_mem = resource["scalar"]["value"]
                self.log.info("MEM %d", offer_mem)

        self.log.debug(
            "Received offer %s with cpus: %s and mem: %s",
            offer["id"]["value"],
            offer_cpus,
            offer_mem,
        )

        remaining_cpus = offer_cpus
        remaining_mem = offer_mem
        
        if (not self.task_queue.empty()):
            key, cmd, executor_config = self.task_queue.get()
            tid = self.task_counter
            self.task_counter += 1

            if "MesosExecutor" in executor_config:
                self.log.debug("Executor Config: %s", executor_config)

                self.task_cpu = executor_config["MesosExecutor"].get("cpus", cpu)
                self.task_mem = executor_config["MesosExecutor"].get("mem_limit", mem)
                image = executor_config["MesosExecutor"].get("image", self.mesos_slave_docker_image)
                force_pull = str(executor_config["MesosExecutor"].get("force_pull", "true")).lower()
                container_type = executor_config["MesosExecutor"].get("container_type", "DOCKER")
                airflow_task_id = executor_config["MesosExecutor"].get("airflow_task_id", None)
            else:
                executor_config = {}
                executor_config["MesosExecutor"] = {}
                executor_config["MesosExecutor"]["airflow_task_id"] = None

            if airflow_task_id is not None:
                # init tasks list for status_update
                self.tasks[airflow_task_id] = None
            else:
                airflow_task_id = "airflow." + str(tid)

            # set the airflow_task_id as executor config
            executor_config["MesosExecutor"]["airflow_task_id"] = airflow_task_id

            # if the resources does not match, add the task again
            if float(remaining_cpus) < float(self.task_cpu):
                self.log.info("Offered CPU's for task %d are not enough: got: %d need: %d - %s", tid, remaining_cpus, self.task_cpu, offer["id"]["value"])
                self.task_queue.put((key, cmd, executor_config))
                return False
            if float(remaining_mem) < float(self.task_mem):
                self.log.info("Offered MEM's for task %d are not enough: got: %d need: %d - %s", tid, remaining_mem, self.task_mem, offer["id"]["value"])
                self.task_queue.put((key, cmd, executor_config))
                return False

            self.task_key_map[airflow_task_id] = key

            self.log.info("Launching task %d using offer %s", tid, offer["id"]["value"])

            name = key.dag_id + "_" + key.task_id + "_" + str(key.execution_date.date()) + ":" + str(key.execution_date.time())

            task = {
                "name": name,
                "task_id": {"value": airflow_task_id},
                "agent_id": {"value": offer["agent_id"]["value"]},
                "resources": [
                    {
                        "name": "cpus",
                        "type": "SCALAR",
                        "scalar": {"value": self.task_cpu},
                    },
                    {
                        "name": "mem",
                        "type": "SCALAR",
                        "scalar": {"value": self.task_mem},
                    },
                ],
                "command": {
                    "shell": self.command_shell,
                    "environment": {
                        "variables": [
                            {
                                "name": "AIRFLOW__CORE__SQL_ALCHEMY_CONN",
                                "value": self.core_sql_alchemy_conn,
                            },
                            {
                                "name": "AIRFLOW__CORE__FERNET_KEY",
                                "value": self.core_fernet_key,
                            },
                            {
                                "name": "AIRFLOW__LOGGING__LOGGING_LEVEL",
                                "value": self.logging_logging_level,
                            },
                        ]
                    },
                    "value": " ".join(cmd),
                },
                "container": {
                    "type": container_type,
                    "volumes": [
                        {
                            "container_path": self.mesos_docker_volume_dag_container_path,
                            "mode": "RW",
                            "source": {
                                "type": "DOCKER_VOLUME",
                                "docker_volume": {
                                    "driver": self.mesos_docker_volume_driver,
                                    "name": self.mesos_docker_volume_dag_name,
                                },
                            },
                        },
                        {
                            "container_path": self.mesos_docker_volume_logs_container_path,
                            "mode": "RW",
                            "source": {
                                "type": "DOCKER_VOLUME",
                                "docker_volume": {
                                    "driver": self.mesos_docker_volume_driver,
                                    "name": self.mesos_docker_volume_logs_name,
                                },
                            },
                        },
                    ],
                    "docker": {
                        "image": image,
                        "force_pull_image": force_pull,
                        "privileged": "true",
                        "parameters": [
                            {
                                "key": "volume",
                                "value": self.mesos_docker_sock
                                + ":/var/run/docker.sock",
                            }
                        ],
                    },
                },
            }

            # concat custom docker environment variables if they are configured
            if len(self.mesos_docker_environment) > 0:
                dockerEnv = ast.literal_eval(self.mesos_docker_environment)
                lenTask = len(dockerEnv)
                i = 0
                while i < lenTask:
                    task["command"]["environment"]["variables"].append(dockerEnv[i])
                    i += 1

            # if the container would be UCR, we can attach tty
            if container_type == "MESOS":
                task["container"]["tty_info"] = {
                    "window_size": {
                        "rows": 80,
                        "columns": 80,
                    },
                }

            option = {"Filters": {"RefuseSeconds": "0.5"}}

            tasks.append(task)
            remaining_cpus -= self.task_cpu
            remaining_mem -= self.task_mem
        if len(tasks) > 0:            
            mesos_offer.accept(tasks, option)
            return True
        else:
            mesos_offer.decline()
            return False

    @provide_session
    def subscribed(self, driver, session=None):
        """
        Subscribe to Mesos Master

        :param driver: Mesos driver object
        """
        # pylint: disable=import-outside-toplevel
        from airflow.models import Connection

        # Update the Framework ID in the database.
        conn_id = FRAMEWORK_CONNID_PREFIX + get_framework_name()
        connection = session.query(Connection).filter_by(conn_id=conn_id).first()
        if connection is None:
            connection = Connection(
                conn_id=conn_id,
                conn_type="mesos_framework-id",
                extra=driver.frameworkId,
            )
        else:
            connection.extra = driver.frameworkId

        self.driver = driver

    def status_update(self, update):
        """Update the Status of the Tasks. Based by Mesos Events."""
        task_id = update["status"]["task_id"]["value"]
        task_state = update["status"]["state"]

        if task_state == "TASK_RUNNING":
            self.log.debug(task_id)
            self.tasks[task_id] = update

        self.log.info("Task %s is in state %s", task_id, task_state)

        key = self.task_key_map[task_id]

        if task_state == "TASK_FINISHED":
            self.result_queue.put((key, State.SUCCESS))
            self.tasks[task_id] = None
            return

        if task_state in ("TASK_LOST", "TASK_KILLED", "TASK_FAILED"):
            self.result_queue.put((key, State.FAILED))
            self.tasks[task_id] = None
            return

    def get_task_info(self, task_id):
        """Return the container_info of the given task_id"""
        if task_id in self.tasks:
            return self.tasks[task_id]

        return None


class MesosExecutor(BaseExecutor):
    """
    MesosExecutor allows distributing the execution of task
    instances to multiple mesos workers.

    Apache Mesos is a distributed systems kernel which abstracts
    CPU, memory, storage, and other compute resources away from
    machines (physical or virtual), enabling fault-tolerant and
    elastic distributed systems to easily be built and run effectively.
    See http://mesos.apache.org/
    """

    class MesosFramework(threading.Thread):
        """MesosFramework class to start the threading"""

        def __init__(self, client):
            super().__init__(target=self)
            self.client = client
            self.stop = False

        def run(self):
            try:
                self.client.register()
            except KeyboardInterrupt:
                print("Stop requested by user, stopping framework....")

    def __init__(self):
        super().__init__()
        self.commands_to_run = []
        self.task_queue = Queue()
        self.result_queue = Queue()
        self.driver = None
        self.client = None
        self.mesos_framework = None
        self.master_urls = None

    @provide_session
    def start(self, session=None):
        """Setup and start routine to connect with the mesos master"""
        master = conf.get("mesos", "MASTER")

        framework_name = get_framework_name()
        framework_id = None
        framework_role = conf.get("mesos", "FRAMEWORK_ROLE", fallback="marathon")

        task_cpu = conf.getfloat("mesos", "TASK_CPU", fallback=0.1)
        task_memory = conf.getint("mesos", "TASK_MEMORY", fallback=256)

        if conf.getboolean("mesos", "CHECKPOINT"):
            framework_checkpoint = True

            if conf.get("mesos", "FAILOVER_TIMEOUT"):
                # Import here to work around a circular import error
                # pylint: disable=import-outside-toplevel
                from airflow.models import Connection

                # Query the database to get the ID of the Mesos Framework, if available.
                conn_id = FRAMEWORK_CONNID_PREFIX + framework_name
                connection = (
                    session.query(Connection).filter_by(conn_id=conn_id).first()
                )
                if connection is not None:
                    # Set the Framework ID to let the scheduler reconnect
                    # with running tasks.
                    framework_id = connection.extra

                # Set Timeout in the case of a mesos master leader change
                framework_failover_timeout = conf.getint("mesos", "FAILOVER_TIMEOUT")

        else:
            framework_checkpoint = False

        self.log.info(
            "MesosFramework master : %s, name : %s, cpu : %d, mem : %d, checkpoint : %s, id : %s",
            master,
            framework_name,
            task_cpu,
            task_memory,
            framework_checkpoint,
            framework_id,
        )

        self.master_urls = "https://" + master

        self.client = MesosClient(
            mesos_urls=self.master_urls.split(","),
            frameworkName=framework_name,
            frameworkId=None,
        )

        self.client.set_role(framework_role)

        if framework_failover_timeout:
            self.client.set_failover_timeout(framework_failover_timeout)
        if framework_checkpoint:
            self.client.set_checkpoint(framework_checkpoint)

        if conf.getboolean("mesos", "AUTHENTICATE"):
            if not conf.get("mesos", "DEFAULT_PRINCIPAL"):
                self.log.error("Expecting authentication principal in the environment")
                raise AirflowException(
                    "mesos.default_principal not provided in authenticated mode"
                )
            if not conf.get("mesos", "DEFAULT_SECRET"):
                self.log.error("Expecting authentication secret in the environment")
                raise AirflowException(
                    "mesos.default_secret not provided in authenticated mode"
                )
            self.client.principal = conf.get("mesos", "DEFAULT_PRINCIPAL")
            self.client.secret = conf.get("mesos", "DEFAULT_SECRET")

        driver = AirflowMesosScheduler(
            self, self.task_queue, self.result_queue, task_cpu, task_memory
        )
        self.driver = driver
        self.client.on(MesosClient.SUBSCRIBED, driver.subscribed)
        self.client.on(MesosClient.UPDATE, driver.status_update)
        self.client.on(MesosClient.OFFERS, driver.resource_offers)
        self.client.on(MesosClient.HEARTBEAT, driver.resource_heartbeat)
        

        self.mesos_framework = MesosExecutor.MesosFramework(self.client)
        self.mesos_framework.start()

        # start the framework api
        app.add_url_rule(
            "/v0/queue_command",
            "queue_command",
            self.api_queue_command,
            methods=["POST"],
        )
        app.add_url_rule(
            "/v0/task/<task_id>",
            "task/<task_id>",
            self.api_get_task_info,
            methods=["GET"],
        )
        app.add_url_rule(
            "/v0/agent/<agent_id>",
            "agent/<agent_id>",
            self.api_get_agent_address,
            methods=["GET"],
        )


        Thread(target=serve, args=[app], daemon=True, kwargs={"port": "10000"}).start()

    def sync(self) -> None:
        """Updates states of the tasks."""
        self.log.debug("Update state of tasks")
        if self.running:
            self.log.debug("self.running: %s", self.running)

        while not self.result_queue.empty():
            results = self.result_queue.get()
            key, state = results
            if key is None:
                return
            if state == "success":
                self.log.info("tasks successfull %s", key)
            if state == "failed":
                self.log.info("tasks failed %s", key)
            self.change_state(*results)

    def execute_async(
        self,
        key: TaskInstanceKey,
        command: CommandType,
        queue: Optional[str] = None,
        executor_config: Optional[Any] = None,
    ):
        """Execute Tasks"""
        self.log.info(
            "Add task %s with command %s with TaskInstance %s",
            key,
            command,
            executor_config,
        )
        self.validate_command(command)
        self.task_queue.put((key, command, executor_config))

    def end(self) -> None:
        """Called when the executor shuts down"""
        self.log.info("Shutting down Mesos Executor")
        # Both queues should be empty...
        self.task_queue = Queue()
        self.result_queue = Queue()
        self.task_queue.join()
        self.result_queue.join()
        self.client.stop = True
        self.driver.tearDown()
        self.mesos_framework.stop = True

    def terminate(self):
        """Terminate the executor is not doing anything."""
        self.end()

    def api_queue_command_error(self, message):
        """Error message handling for queue_command"""
        self.log.error(message)

        return message

    def api_queue_command(self):
        """
        Queue Command via API

        Example: curl --header "Content-Type: application/json" -X POST -d
        '{ "command": "test", "image": "alpine" }' 127.0.0.1:10000/v0/queue_command
        """

        data = json.loads(request.data)
        error, command = None, None

        if "command" in data:
            command = data["command"]
        else:
            error = self.api_queue_command_error(
                "Expecting command in queue_command call"
            )

        if error is not None:
            response = Response(error, status=400, headers={})
        else:
            self.log.info("Queue task with command %s and %s", command, data)
            self.task_queue.put((None, command, data))
            response = Response("Ok", status=200, headers={})
        # Send it
        return response

    def api_get_task_info(self, task_id):
        """
        Get Mesos TASK Info via API

        Example: curl -X GET 127.0.0.1:10000/v0/task/<task_id>
        """
        task_info = self.driver.get_task_info(task_id)

        response = Response(
            json.dumps(task_info), status=200, mimetype="application/json"
        )
        return response

    def api_get_agent_address(self, agent_id):
        """
        Given a master and an agent id, return the agent address
        by checking the /slaves endpoint of the master.
        """

        http = urllib3.PoolManager()
        http_response = http.request(
            "GET",
            self.master_urls + "/master/slaves",
            headers=self.authentication_header(),
            timeout=5,
        )
        data = http_response.data.decode("utf-8")

        if data is not None:
            data = json.loads(data)
            for agent in data["slaves"]:
                if agent["id"] == agent_id:
                    data = {"hostname": agent["hostname"], "port": str(agent["port"])}
                    response = Response(
                        json.dumps(data), status=200, mimetype="application/json"
                    )
                    return response

        response = Response(None, status=200, mimetype="application/json")
        return response

    def authentication_header(self):
        """
        Return the BasicAuth authentication header
        """
        if self.client.principal is not None and self.client.secret is not None:
            headers = urllib3.make_headers(
                basic_auth=self.client.principal + ":" + self.client.secret
            )
            return headers
        return None
