from qm.pb.frontend_pb2 import SimulationRequest
from qm.simulate.interface import SimulatorInterface


class RawInterface(SimulatorInterface):
    """
    Creates a raw interface for use in :class:`~qm.simulate.interface.SimulationConfig`.
    A raw interface defines samples that will be inputted into the OPX inputs.

    :param list connections:

        List of tuples with the connection. Each tuple should be:

                ``(toController: str, toPort: int, toSamples: List[float])``
    :param float noisePower: How much noise to add to the input.

    Example::

    >>> job = qmm.simulate(config, prog, SimulationConfig(
    >>>                   duration=20000,
    >>>                   # 500 ns of DC 0.2 V into con1 input 1
    >>>                   simulation_interface=RawInterface([("con1", 1, [0.2]*500)])
    """

    def __init__(self, connections, noisePower=0.0):

        if (
            type(noisePower) is not float and type(noisePower) is not int
        ) or noisePower < 0:
            raise Exception("noisePower must be a positive number")

        self.noisePower = noisePower

        if type(connections) is not list:
            raise Exception("connections argument must be of type list")

        self.connections = list()
        for connection in connections:
            if type(connection) is not tuple:
                raise Exception("each connection must be of type tuple")
            if len(connection) == 3:
                if (
                    type(connection[0]) is not str
                    or type(connection[1]) is not int
                    or type(connection[2]) is not list
                ):
                    raise Exception(
                        "connection should be (fromController, fromPort, toSamples)"
                    )
                self.connections.append(connection)
            else:
                raise Exception("connection should be tuple of length 3 or 4")

    def update_simulate_request(self, request: SimulationRequest):
        request.simulate.simulationInterface.raw.SetInParent()
        request.simulate.simulationInterface.raw.noisePower = self.noisePower
        for connection in self.connections:
            con = request.simulate.simulationInterface.raw.connections.add()
            con.fromController = connection[0]
            con.fromPort = connection[1]
            con.toSamples.extend(connection[2])
