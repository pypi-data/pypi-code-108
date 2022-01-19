from qm.pb.frontend_pb2 import SimulationRequest
from qm.simulate.interface import SimulatorInterface


class LoopbackInterface(SimulatorInterface):
    """
    Creates a loopback interface for use in
    :class:`~qm.simulate.interface.SimulationConfig`.
    A loopback connects the output of the OPX into it's input. This can be defined
    directly using the ports or through the elements.

    :param list connections:

        List of tuples with loopback connections. Each tuple can be:

            1. Physical connection between ports:

                ``(fromController: str, fromPort: int, toController: str, toPort: int)``

            2. Virtual connection between quantum elements:

                ``(fromQE: str, toQE: str, toQEInput: int)``
    :param int latency: The latency between the OPX outputs and its input.
    :param float noisePower: How much noise to add to the input.

    Example::

    >>> job = qmm.simulate(config, prog, SimulationConfig(
    >>>                   duration=20000,
    >>>                   # loopback from output 1 to input 2 of controller 1:
    >>>                   simulation_interface=LoopbackInterface([("con1", 1, "con1", 2)])
    """

    def __init__(self, connections, latency=24, noisePower=0.0):
        if type(latency) is not int or latency < 0:
            raise Exception("latency must be a positive integer")

        self.latency = latency

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
            if len(connection) == 4:
                if (
                    type(connection[0]) is not str
                    or type(connection[1]) is not int
                    or type(connection[2]) is not str
                    or type(connection[3]) is not int
                ):
                    raise Exception(
                        "connection should be (fromController, fromPort, toController, toPort)"
                    )
                self.connections.append(connection)
            elif len(connection) == 3:
                if (
                    type(connection[0]) is not str
                    or type(connection[1]) is not str
                    or type(connection[2]) is not int
                ):
                    raise Exception("connection should be (fromQE, toQE, toQEInput)")
                self.connections.append(
                    (connection[0], -1, connection[1], connection[2])
                )
            else:
                raise Exception("connection should be tuple of length 3 or 4")

    def update_simulate_request(self, request: SimulationRequest):
        request.simulate.simulationInterface.loopback.SetInParent()
        request.simulate.simulationInterface.loopback.latency = self.latency
        request.simulate.simulationInterface.loopback.noisePower = self.noisePower
        for connection in self.connections:
            con = request.simulate.simulationInterface.loopback.connections.add()
            con.fromController = connection[0]
            con.fromPort = connection[1]
            con.toController = connection[2]
            con.toPort = connection[3]
