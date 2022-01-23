from dataclasses import dataclass
from typing import Union, TypeVar, Generic, NewType, List

from qm.pb.frontend_pb2 import SimulationRequest


class SimulationConfig(object):
    """
    Creates a configuration object to pass to
    :func:`~qm.QuantumMachinesManager.QuantumMachinesManager.simulate`

    :param int duration: The duration to run the simulation for, in clock cycles
    :param bool include_analog_waveforms: True to collect simulated analog waveform names
    :param bool include_digital_waveforms: True to collect simulated digital waveform names
    :param SimulatorInterface simulation_interface:

        Interface for to simulator. Currently supported interfaces:

            ``None`` - Zero inputs

            :class:`~qm.simulate.loopback.LoopbackInterface` - Loopback output to input

            :class:`~qm.simulate.raw.RawInterface` - Specify samples for inputs

    :param  List[ControllerConnection] controller_connections: A list of connections
        between the controllers in the config
    :param int extraProcessingTimeoutInMs: timeout in ms to wait for stream processing
        to finish. Default is -1, which is disables the timeout
    """

    duration = 0
    simulate_analog_outputs = False

    def __init__(
        self,
        duration=0,
        include_analog_waveforms=False,
        include_digital_waveforms=False,
        simulation_interface=None,
        controller_connections: List["ControllerConnection"] = None,
        extraProcessingTimeoutInMs=-1,
    ):
        if controller_connections is None:
            controller_connections = []
        super(SimulationConfig, self).__init__()
        self.duration = duration
        self.include_analog_waveforms = include_analog_waveforms is True
        self.include_digital_waveforms = include_digital_waveforms is True
        self.simulation_interface = simulation_interface
        self.controller_connections = controller_connections
        self.extraProcessingTimeoutInMs = extraProcessingTimeoutInMs

    def update_simulate_request(self, request: SimulationRequest):
        if self.simulation_interface is None:
            request.simulate.simulationInterface.none.SetInParent()
        else:
            self.simulation_interface.update_simulate_request(request)


class SimulatorInterface(object):
    def update_simulate_request(self, request: SimulationRequest):
        pass


@dataclass
class InterOpxAddress:
    """
    :param str controller: The name of the controller
    :param bool is_left_connection:
    """

    controller: str
    is_left_connection: bool


@dataclass
class InterOpxChannel:
    """
    :param str controller: The name of the controller
    :param int channel_number:
    """

    controller: str
    channel_number: int


InterOpxPairing = NewType("InterOpxPairing", Union[InterOpxAddress, InterOpxChannel])
T = TypeVar("T", InterOpxPairing, InterOpxPairing)


class ControllerConnection(Generic[T]):
    """"""

    def __init__(self, source: T, target: T):
        self.source = source
        self.target = target
