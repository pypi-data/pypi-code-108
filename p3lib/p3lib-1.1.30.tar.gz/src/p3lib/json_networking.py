#!/usr/bin/env python3

import  socketserver
import  socket
from    struct import pack, unpack
import  json
from    time import  sleep

class JSONNetworking(Exception):
    pass

class JSONServer(socketserver.ThreadingTCPServer):
    """@brief Responsible for accepting tcp connections to receive and send json messages."""

    daemon_threads = True
    allow_reuse_address = True

class JsonServerHandler (socketserver.BaseRequestHandler):

    LEN_FIELD               = 4
    DEFAULT_RX_POLL_SECS    = 0.02
    DEFAULT_RX_BUFFER_SIZE  = 2048

    @staticmethod
    def DictToJSON(aDict):
        """@brief convert a python dictionary into JSON text
           @param aDict The python dictionary to be converted
           @return The JSON text representing aDict"""
        return json.dumps(aDict)

    @staticmethod
    def JSONToDict(jsonText):
        """@brief Convert from JSON text to a python dict. Throws a ValueError
                  if the text is formatted incorrectly.
           @param jsonText The JSON text to be converted to a dict
           @return a python dict object"""
        return json.loads(jsonText)

    @staticmethod
    def TX(request, theDict):
        """@brief Write the dict to the socket as json text
           @param request The request object passed from the handle() method.
           @theDict The python dictionary to send."""
        if request:
            msg = JsonServerHandler.DictToJSON(theDict).encode()
            sFmt = ">%ds" % len(msg)
            body = pack(sFmt, msg)
            bodyLen = pack('>I', len(body))
            txBuf = bodyLen + body
            request.send(txBuf)

        else:
            raise RuntimeError("TX socket error")

    @staticmethod
    def GetBodyLen(rxBytes):
        """@brief Get the length of the body of the message.
           @param rxBytes The rx buffer containing bytes received.
           @return The length of the body of the message or 0 if we do not have a complete message in the rx buffer."""
        bodyLenFound = 0
        #If we have enough data to extract the length field (start of PDU)
        if len(rxBytes) >= JsonServerHandler.LEN_FIELD:
            # Read the length of the message
            bodyLen = unpack(">I", rxBytes[:JsonServerHandler.LEN_FIELD])[0]
            #If we have the len field + the message body
            if len(rxBytes) >= JsonServerHandler.LEN_FIELD+bodyLen:
                bodyLenFound = bodyLen
        return bodyLenFound

    @staticmethod
    def MsgAvail(rxBytes):
        """@brief Determine is a complete message is present in the rx buffer.
           @param rxBytes The rx buffer containing bytes received.
           @return True if a complete message is present in the RX buffer."""
        msgAvail = False

        bodyLen = JsonServerHandler.GetBodyLen(rxBytes)

        if bodyLen:
            msgAvail = True

        return msgAvail

    def tx(self, request, theDict, throwError=True):
        """@brief send a python dictionary object to the client via json.
           @param request The request object to send data on.
           @param theDict The dictionary to send
           @param throwError If True then an exception will be thrown if an error occurs.
                              If False then this method will fail silentley.
           @return True on success. False on failure if throwError = False"""
        try:
            JsonServerHandler.TX(request, theDict)
            return True
        except:
            if throwError:
                raise
            return False

    def _getDict(self):
        """@brief Get dict from rx data.
           @return The oldest dict in the rx buffer."""
        rxDict = None
        bodyLen = JsonServerHandler.GetBodyLen(self._rxBuffer)
        #If we have a complete message in the RX buffer
        if bodyLen > 0:
            body = self._rxBuffer[JsonServerHandler.LEN_FIELD:JsonServerHandler.LEN_FIELD+bodyLen]
            rxDict = JsonServerHandler.JSONToDict( body.decode() )
            #Remove the message just received from the RX buffer
            self._rxBuffer = self._rxBuffer[JsonServerHandler.LEN_FIELD+bodyLen:]

        return rxDict

    def rx(self, blocking=True,
                 pollPeriodSeconds=DEFAULT_RX_POLL_SECS,
                 rxBufferSize=DEFAULT_RX_BUFFER_SIZE):
        """@brief Get a python dictionary object from the server.
           @param blocking If True block until complete message is received.
           @param pollPeriodSeconds If blocking wait for this period in seconds between checking for RX data.
           @param rxBufferSize The size of the receive buffer in bytes.
           @return A received dictionary of None if not blocking and no dictionary is available."""
        #If we don't have an rx buffer, create one.
        if '_rxBuffer' not in dir(self):
            self._rxBuffer = bytearray()

        while not JsonServerHandler.MsgAvail(self._rxBuffer):

            try:
                rxd = self.request.recv(rxBufferSize)
                if len(rxd) > 0:
                    self._rxBuffer = self._rxBuffer + rxd
                else:
                    raise RuntimeError("Socket closed")

                if not blocking:
                    break

            except BlockingIOError:
                if not blocking:
                    break

            if blocking:
                sleep(pollPeriodSeconds)

        return self._getDict()

    def handle(self):
        """@brief Handle connections to the server."""
        raise JSONNetworking("!!! You must override this method in a subclass !!!")

class JSONClient(object):

    def __init__(self, address, port, keepAliveActSec=1, keepAliveTxSec=15, keepAliveFailTriggerCount=8):
        """@brief Connect to a JSONServer socket.
                  If on a Linux system then the connection will apply a keepalive to the TCP connection.
                  By default this is 2 minutes.
           @param address The address of the JSONServer.
           @param The port on the JSON server to connect to.
           @param keepAliveActSec Activate the keepalive failure this many seconds after it is triggered.
           @param keepAliveTxSec Send a TCP keepalive periodically. This defines the period in seconds.
           @param keepAliveFailTriggerCount Trigger a keepalive failure when this many keepalives fail consecutively."""

        self._socket = socket.socket()
        self._socket.connect( (address, port) )

        if hasattr(socket, 'SOL_SOCKET') and\
           hasattr(socket, 'SO_KEEPALIVE') and\
           hasattr(socket, 'IPPROTO_TCP') and\
           hasattr(socket, 'TCP_KEEPIDLE') and\
           hasattr(socket, 'TCP_KEEPINTVL') and\
           hasattr(socket, 'TCP_KEEPCNT'):
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, keepAliveActSec)
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, keepAliveTxSec)
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, keepAliveFailTriggerCount)
        self._socket.setblocking(False)
        self._rxBuffer = bytearray()

    def tx(self, theDict, throwError=True):
        """@brief send a python dictionary object to the server via json
           @param theDict The dictionary to send
           @param throwError If True then an exception will be thrown if an error occurs.
                              If False then this method will fail silentley.
           @return True on success. False on failure if throwError = False"""
        try:
            JsonServerHandler.TX(self._socket, theDict)
            return True
        except:
            if throwError:
                raise
            return False

    def _getDict(self):
        """@brief Get dict from rx data.
           @return The oldest dict in the rx buffer."""
        rxDict = None
        bodyLen = JsonServerHandler.GetBodyLen(self._rxBuffer)
        #If we have a complete message in the RX buffer
        if bodyLen > 0:
            body = self._rxBuffer[JsonServerHandler.LEN_FIELD:JsonServerHandler.LEN_FIELD+bodyLen]
            rxDict = JsonServerHandler.JSONToDict( body.decode() )
            #Remove the message just received from the RX buffer
            self._rxBuffer = self._rxBuffer[JsonServerHandler.LEN_FIELD+bodyLen:]

        return rxDict

    def rx(self, blocking=True,
                 pollPeriodSeconds=JsonServerHandler.DEFAULT_RX_POLL_SECS,
                 rxBufferSize=JsonServerHandler.DEFAULT_RX_BUFFER_SIZE):
        """@brief Get a python dictionary object from the server.
           @param blocking If True block until complete message is received.
           @param pollPeriodSeconds If blocking wait for this period in seconds between checking for RX data.
           @param rxBufferSize The size of the receive buffer in bytes.
           @return A received dictionary of None if not blocking and no dictionary is available."""

        while not JsonServerHandler.MsgAvail(self._rxBuffer):

            try:
                rxd = self._socket.recv(rxBufferSize)
                if len(rxd) > 0:
                    self._rxBuffer = self._rxBuffer + rxd
                else:
                    raise RuntimeError("Socket closed")

                if not blocking:
                    break

            except BlockingIOError:
                if not blocking:
                    break

            if blocking:
                sleep(pollPeriodSeconds)

        return self._getDict()

    def close(self):
        """@brief Close the socket connection to the server."""
        if self._socket:
            self._socket.close()
