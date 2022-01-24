#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tools for OPC testing

NOTE: After a variable is set for the first time, the type is fixed! This can usually
happen for numerical values. Therefore, we should always use 'float' as datatype for
numerical variables.

GOOD:
demo_opcua_server.set_var(constants.Power.voltage_target, 0.0)

BAD:
demo_opcua_server.set_var(constants.Power.voltage_target, 0)
"""

from asyncua.ua import NodeId, Variant

from hvl_ccb.comm.opc import Server
from hvl_ccb.dev.cube import constants


class DemoServer(Server):

    def __init__(
        self, namespace,
            cube_type: constants._CubeOpcEndpoint,
            port: int = 4840,
            shelffile=None,
            iserver=None,
    ):
        super().__init__(shelffile, iserver)

        self.set_endpoint(f"opc.tcp://0.0.0.0:{port}/freeopcua/server/")

        self._ns = namespace

        # TODO remove after deleting supercube2015
        if type(cube_type) == constants._CubeOpcEndpoint:
            self._cube_type = cube_type.value
        else:
            self._cube_type = cube_type

        self._root = self.get_objects_node().add_object(
            self._ns, self._cube_type
        )

    def set_var(self, id, val):
        """
        Set a variable with the `id` to `val`. If it does not yet exist -> add_variable
        """

        nodeid = NodeId(Identifier=str(id), NamespaceIndex=self._ns)

        if id in [node.nodeid.Identifier for node in self._root.get_variables()]:
            self.get_node(nodeid).set_value(Variant(val))
        else:
            variable = self._root.add_variable(nodeid, str(id), Variant(val))
            variable.set_writable(True)

    def get_var(self, id):
        return self.get_node(
            NodeId(Identifier=str(id), NamespaceIndex=self._ns),
        ).get_value()
