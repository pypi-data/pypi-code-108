# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for SynapseComm."""

import json

from .telemetryutils import set_client


class SynapseComm:
    """SynapseComm is responsible to the Communication between Juypter backend and frontend."""

    # Refer https://jupyter-notebook.readthedocs.io/en/stable/comms.html for details
    _comm = None
    _client_info = None

    @staticmethod
    def register_comm(ipython):
        """Register the Comm instance crated by frontend."""
        # frontend creates the Comm, backend uses it for communication
        ipython.kernel.comm_manager.register_target("SynapseSparkMonitor", SynapseComm._register_comm_callback)

    @staticmethod
    def send(msg):
        """Send message to frontend."""
        if SynapseComm._comm is not None:
            SynapseComm._comm.send({"msgtype": "fromlivy", "msg": json.dumps(msg)})
        else:
            # For local debug
            # print(json.dumps(msg))
            pass

    @staticmethod
    def _register_comm_callback(comm, msg):
        SynapseComm._comm = comm  # _comm is the frontend Comm instance
        if msg and msg.get("content") and msg.get("content").get("data"):
            # msg.content.data contains msgtype, clienttype and clientid
            SynapseComm.set_client_info(msg.get("content").get("data"))

        @SynapseComm._comm.on_msg
        def _receive(msg_receive):
            SynapseComm.set_client_info(msg_receive)

        @SynapseComm._comm.on_close
        def _close(msg_close):
            SynapseComm._comm = None
            SynapseComm._client_info = None

    @staticmethod
    def set_client_info(msg):
        """Set the client info."""
        if msg.get("msgtype") == "FrontEndStart":
            SynapseComm._client_info = msg
            set_client(msg.get("clienttype"), msg.get("clientid"))
