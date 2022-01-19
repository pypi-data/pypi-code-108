import json
import grpc

from qm.QmJob import QmJob
from qm._errors import FailedToExecuteJobException
from qm.program._qua_config_schema import _validate_config_capabilities
from qm.server_detector import detect_server
from qm.utils import _level_map, _set_compiler_options
from qm import _Program
from qm.logger import logger

from qm.QuantumMachine import QuantumMachine
from qm.pb import frontend_pb2_grpc
from google.protobuf import empty_pb2

from qm.pb.frontend_pb2 import (
    ResetDataProcessingRequest,
    SimulationRequest,
    PerformHalDebugCommandRequest,
)
from qm.pb.qm_manager_pb2 import OpenQuantumMachineRequest, GetQuantumMachineRequest
from qm._controller import Controller
from qm.persistence import SimpleFileStore, BaseStore
from qm.program import load_config
from qm._user_config import load_user_config
from qm.program.ConfigBuilder import convert_msg_to_config
from qm.simulate.interface import (
    SimulationConfig,
    InterOpxAddress,
    InterOpxChannel,
)


class QuantumMachinesManager(object):
    def __init__(self, host=None, port=None, **kargs):
        """
        :param string host: Host where to find the QM orchestrator. If ``None``, local settings are used
        :param port: Port where to find the QM orchestrator. If None, local settings are used
        """
        super(QuantumMachinesManager, self).__init__()
        self._log = logger

        config = load_user_config()
        if host is None:
            host = config.manager_host

        credentials = kargs.get("credentials", None)
        user_token = config.user_token
        server_details, tried_ports = detect_server(
            user_token=user_token,
            credentials=credentials,
            host=host,
            port_from_user_config=config.manager_port,
            user_provided_port=port,
        )

        if server_details is None:
            message = (
                "Failed to connect to QuantumMachines server. Tried connecting to %s"
                % ",".join([f"{host}:{port}" for port in tried_ports])
            )
            self._log.error(message)
            raise Exception(message)

        store: BaseStore = kargs.get("store")
        if not isinstance(store, BaseStore):
            root = kargs.get("file_store_root", ".")
            store = SimpleFileStore(root)
        self._store = store

        self._server_details = server_details
        self._caps = server_details.capabilities
        self._channel = intercept_channel = server_details.grpc_channel
        self._frontend = frontend_pb2_grpc.FrontendStub(intercept_channel)

        raise_on_error = config.strict_healthcheck is not False
        if "log_level" in kargs:
            new_level = kargs.get("log_level")
            try:
                logger.setLevel(new_level)
            except ValueError:
                logger.warning(
                    "Failed to set log level. level '%s' is not recognized", new_level
                )
        self.perform_healthcheck(raise_on_error)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close()
        return False

    @property
    def store(self) -> BaseStore:
        return self._store

    def perform_healthcheck(self, strict=True):
        """
        Perform a health check against the QM server.

        :param strict: Will raise an exception if health check failed
        """
        with _grpc_context():
            self._log.info("Performing health check")
            req = empty_pb2.Empty()
            res = self._frontend.HealthCheck(req)

            for msg in res.warningMessages:
                self._log.warning("  HC Warning: " + msg)

            if res.ok:
                self._log.info("Health check passed")
            else:
                self._log.error("Health check FAILED!")
                for msg in res.message:
                    self._log.error("  HC Error: " + msg)

                for msg in res.errorMessages:
                    self._log.error("  HC Error: " + msg)
                if strict:
                    raise Exception("Health check failed")

    def version(self):
        """
        :return: The SDK and QOP versions
        """
        server_version = self._server_details.qop_version
        from qm.version import __version__

        return {"client": __version__, "server": server_version}

    def reset_data_processing(self):
        """
        Stops current data processing for ALL running jobs
        """
        with _grpc_context():
            req = ResetDataProcessingRequest()
            self._frontend.ResetDataProcessing(req)

    def close(self):
        """Closes the Quantum machine manager"""
        self._close()

    def _close(self):
        self._channel.close()

    def open_qm(self, config, close_other_machines=True):
        """
        Opens a new quantum machine. A quantum machine can use multiple OPXes, and a
        single OPX can also be used by multiple quantum machines as long as they do not
        share the same physical resources (input/output ports) as defined in the config.

        :param config: The config that will be used by the quantum machine
        :param close_other_machines: When set to to true (default) any open quantum
                            machines will be closed. This simplify the workflow,
                            but does not enable opening more than one quantum machine.
        :return: A quantum machine obj that can be used to execute programs
        """

        loaded_config = load_config(config)
        _validate_config_capabilities(loaded_config, self._caps)

        return self._open_qm_pb(loaded_config, close_other_machines)

    def _open_qm_pb(self, pb_config, close_other_machines=False):
        with _grpc_context():
            request = OpenQuantumMachineRequest()

            if close_other_machines:
                request.always = True
            else:
                request.never = True

            request.config.CopyFrom(pb_config)

            result = self._frontend.OpenQuantumMachine(request)
            if not result.success:
                exception = Exception("Can not open QM. Please see previous errors")
                for err in result.configValidationErrors:
                    self._log.error(
                        'CONFIG ERROR in key "%s" [%s] : %s',
                        err.path,
                        err.group,
                        err.message,
                    )

                for err in result.physicalValidationErrors:
                    self._log.error(
                        'PHYSICAL CONFIG ERROR in key "%s" [%s] : %s',
                        err.path,
                        err.group,
                        err.message,
                    )

                exception.errors = [
                    (it.group, it.path, it.message)
                    for it in result.configValidationErrors
                ]
                exception.errors += [
                    (it.group, it.path, it.message)
                    for it in result.physicalValidationErrors
                ]

                raise exception

            parsed_config = convert_msg_to_config(request.config)
            return QuantumMachine(result.machineID, request.config, parsed_config, self)

    def open_qm_from_file(self, filename, close_other_machines=True):
        """
        Opens a new quantum machine with config taken from a file on the local file system

        :param filename: The path to the file that contains the config
        :param close_other_machines: Flag whether to close all other running machines
        :return: A quantum machine obj that can be used to execute programs
        """
        with open(filename) as json_file:
            json1_str = json_file.read()

            def remove_nulls(d):
                return {k: v for k, v in d.items() if v is not None}

            config = json.loads(json1_str, object_hook=remove_nulls)
        return self.open_qm(config, close_other_machines)

    def simulate(self, config, program, simulate, **kwargs):
        """
        Simulate the outputs of a deterministic QUA program.

        The following example shows a simple execution of the simulator, where the
        associated config object is omitted for brevity.

        Example::

            >>> from qm.QuantumMachinesManager import QuantumMachinesManager
            >>> from qm.qua import *
            >>> from qm import SimulationConfig
            >>>
            >>> qmm = QuantumMachinesManager()
            >>>
            >>> with program() as prog:
            >>>     play('pulse1', 'qe1')
            >>>
            >>> job = qmm.simulate(config, prog, SimulationConfig(duration=100))

        :param config: A QM config
        :param program: A QUA ``program()`` object to execute
        :param simulate: A ``SimulationConfig`` configuration object
        :param kwargs: additional parameters to pass to execute
        :return: a ``QmJob`` object (see QM Job API).
        """

        if type(program) is not _Program:
            raise Exception("program argument must be of type qm.program.Program")

        with _grpc_context():
            request = SimulationRequest()
            msg_config = load_config(config)
            request.config.CopyFrom(msg_config)

            if type(simulate) is SimulationConfig:
                request.simulate.SetInParent()
                request.simulate.duration = simulate.duration
                request.simulate.includeAnalogWaveforms = (
                    simulate.include_analog_waveforms
                )
                request.simulate.includeDigitalWaveforms = (
                    simulate.include_digital_waveforms
                )
                request.simulate.extraProcessingTimeoutMs = (
                    simulate.extraProcessingTimeoutInMs
                )
                simulate.update_simulate_request(request)

                for connection in simulate.controller_connections:
                    con = request.controllerConnections.add()

                    if type(connection.source) is not type(connection.target):
                        raise Exception(
                            f"Unsupported InterOpx connection. Source is "
                            f"{type(connection.source).__name__} but target is "
                            f"{type(connection.target).__name__}"
                        )

                    if isinstance(connection.source, InterOpxAddress):
                        con.addressToAddress.SetInParent()
                        con.addressToAddress.source.SetInParent()
                        con.addressToAddress.source.controller = (
                            connection.source.controller
                        )
                        con.addressToAddress.source.left = (
                            connection.source.is_left_connection
                        )
                        con.addressToAddress.target.SetInParent()
                        con.addressToAddress.target.controller = (
                            connection.target.controller
                        )
                        con.addressToAddress.target.left = (
                            connection.target.is_left_connection
                        )
                    elif isinstance(connection.source, InterOpxChannel):
                        con.channelToChannel.SetInParent()
                        con.channelToChannel.source.SetInParent()
                        con.channelToChannel.source.controller = (
                            connection.source.controller
                        )
                        con.channelToChannel.source.channelNumber = (
                            connection.source.channel_number
                        )
                        con.channelToChannel.target.SetInParent()
                        con.channelToChannel.target.controller = (
                            connection.target.controller
                        )
                        con.channelToChannel.target.channelNumber = (
                            connection.target.channel_number
                        )
                    else:
                        raise Exception(
                            f"Unsupported InterOpx connection. Source is "
                            f"{type(connection.source).__name__}. Supported types are "
                            f"InterOpxAddress "
                            f"or InterOpxChannel"
                        )

            request.highLevelProgram.CopyFrom(program.build(msg_config))
            _set_compiler_options(request, **kwargs)

            logger.info("Simulating program")

            response = self._frontend.Simulate(request)

            messages = [
                (_level_map[msg.level], msg.message) for msg in response.messages
            ]

            config_messages = [
                (_level_map[msg.level], msg.message)
                for msg in response.configValidationErrors
            ]

            job_id = response.jobId

            for lvl, msg in messages:
                logger.log(lvl, msg)

            for lvl, msg in config_messages:
                logger.log(lvl, msg)

            if not response.success:
                logger.error("Job " + job_id + " failed. Failed to execute program.")
                for error in response.simulated.errors:
                    logger.error(f"Simulation error: {error}")
                raise FailedToExecuteJobException(job_id)

            return QmJob(self, job_id, response)

    def list_open_quantum_machines(self):
        """
        Return a list of open quantum machines. (Returns only the ids, use ``get_qm(...)`` to get the machine object)

        :return: The ids list
        """
        with _grpc_context():
            request = empty_pb2.Empty()
            open_qms = []
            for qm_id in self._frontend.ListOpenQuantumMachines(request).machineIDs:
                open_qms.append(qm_id)
            return open_qms

    def get_qm(self, machine_id):
        """
        Gets an open quantum machine object with the given machine id

        :param machine_id: The id of the open quantum machine to get
        :return: A quantum machine obj that can be used to execute programs
        """
        with _grpc_context():
            request = GetQuantumMachineRequest()
            request.machineID = machine_id
            result = self._frontend.GetQuantumMachine(request)
            if not result.success:
                self._raise_get_qm_errors(result)
            parsed_config = convert_msg_to_config(result.config)
            return QuantumMachine(result.machineID, result.config, parsed_config, self)

    def _get_qm_config(self, machine_id):
        with _grpc_context():
            request = GetQuantumMachineRequest()
            request.machineID = machine_id
            result = self._frontend.GetQuantumMachine(request)
            if not result.success:
                self._raise_get_qm_errors(result)
            return {
                "pb_config": result.config,
                "config": convert_msg_to_config(result.config),
            }

    def _raise_get_qm_errors(self, result):
        error_str = ""
        for err in result.errors:
            error_str = error_str + err.message + "\n"
        exception = Exception(error_str)
        exception.errors = [(it.code, it.message) for it in result.errors]
        raise exception

    def close_all_quantum_machines(self):
        """
        Closes ALL open quantum machines
        """
        with _grpc_context():
            request = empty_pb2.Empty()
            result = self._frontend.CloseAllQuantumMachines(request)
            if not result.success:
                exception = Exception(
                    "Can not close all quantum machines. Please see previous errors"
                )
                for err in result.errors:
                    self._log.error(err.message)

                exception.errors = [(it.code, it.message) for it in result.errors]
                raise exception

    def get_controllers(self):
        """
        Returns a list of all the controllers that are available
        """
        with _grpc_context():
            request = empty_pb2.Empty()
            result = self._frontend.GetControllers(request)
            controllers_list = []
            for controller in result.controllers:
                controllers_list.append(Controller.build_from_message(controller))
            return controllers_list

    def validate_version(self, host):
        # SDK version is not coupled to a specific version anymore.
        # We check for capabilities
        pass

    def clear_all_job_results(self):
        """
        Deletes all data from all previous jobs
        """
        with _grpc_context():
            request = empty_pb2.Empty()
            self._frontend.ClearAllJobResults(request)

    def _send_debug_command(self, controller_name, command):
        with _grpc_context():
            request = PerformHalDebugCommandRequest()
            request.controllerName = controller_name
            request.command = command
            response = self._frontend.PerformHalDebugCommand(request)
            if not response.success:
                raise Exception(response.response)
            return response.response


class _grpc_context(object):
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None and issubclass(exc_type, grpc.RpcError):
            # raise RuntimeError("Failed to contact QM manager")
            try:
                print(exc_val)
                details = ": " + exc_val.details()
            except RuntimeError as e:
                print(e)
                details = ""
            raise RuntimeError("Failed to contact QM manager" + details)
        pass
