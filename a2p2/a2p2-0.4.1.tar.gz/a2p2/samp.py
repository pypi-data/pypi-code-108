#!/usr/bin/env python

__all__ = []

from astropy.samp import SAMPIntegratedClient
from os import sep
import logging

logger = logging.getLogger(__name__)

class Receiver(object):

    def __init__(self, client):
        self.client = client
        self.received = False

    def receive_call(self, private_key, sender_id, msg_id, mtype, params, extra):
        self.mtype=mtype
        self.params = params
        self.received = True
        self.client.reply(
            msg_id, {"samp.status": "samp.ok", "samp.result": {}})

    def receive_notification(self, private_key, sender_id, mtype, params, extra):
        self.mtype=mtype
        self.params = params
        self.received = True

    def clear(self):
        self.received = False
        self.params = None

    def get_last_message(self):
        pass  # TODO handle here a buffer ...


class A2p2SampClient():
    # TODO watch hub disconnection

    def __init__(self):
        self.sampClient = SAMPIntegratedClient(
            "A2P2 samp relay")  # TODO get title from main program class instead of HardCoded value

    def __del__(self):
        self.disconnect()

    def connect(self):
        self.sampClient.connect()
        # an error is thrown here if no hub is present

        # TODO get samp client name and display it in the UI
        # TODO !! declare mtypes as enum

        # Instantiate the receiver
        self.r = Receiver(self.sampClient)
        # Listen for any instructions to load a table
        self.sampClient.bind_receive_call("ob.load.data", self.r.receive_call)
        self.sampClient.bind_receive_notification(
            "ob.load.data", self.r.receive_notification)
        # Listen for Model related instructions
        self.sampClient.bind_receive_call("fr.jmmc.litpro.start.setting",self.r.receive_call)
        self.sampClient.bind_receive_notification(
            "fr.jmmc.litpro.start.setting",self.r.receive_notification)

    def disconnect(self):
        self.sampClient.disconnect()

    def is_connected(self):
        # Workarround the 'non' reliable is_connected attribute
        # this helps to reconnect after hub connection lost
        try:
            return self.sampClient.is_connected and (self.sampClient.ping() or self.sampClient.is_connected)
        except:
            # consider connection refused exception as not connected state
            return False

    def get_status(self):
        if self.is_connected():
            return "connected [%s]" % (self.sampClient.get_public_id())
        else:
            return "not connected"

    def get_public_id(self):
        return self.sampClient.get_public_id()

    def has_message(self):
        return self.is_connected() and self.r.received

    def clear_message(self):
        return self.r.clear()

    def has_ob_message(self):
        return "ob.load.data" in self.r.mtype

    def get_ob_url(self):
        url = self.r.params['url']
        if url.startswith("file:///"):
            if sep == '/':
                return url[7:]
            else:
                return url[8:] # Do not leave leading / on windows machines for file:///C:/Users....
        elif url.startswith("file:/"):  # work arround bugged file urls on *nix
            return url[5:]
        return url

    def has_model_message(self):
        return "fr.jmmc.litpro.start.setting" in self.r.mtype

    def get_model(self):
        return self.r.params['model']

