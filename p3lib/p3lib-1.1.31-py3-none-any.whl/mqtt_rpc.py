#!/usr/bin/python3

import  paho.mqtt.client as mqtt
from    abc import abstractmethod
import  json
import  traceback
from    threading import Condition
from    queue import Queue

class MQTTError(Exception):
  pass

class MQTTRPCClient(object):

    DEFAULT_HOST                = "localhost"
    DEFAULT_PORT                = 1883
    DEFAULT_KEEPALIVE_SECONDS   = 60
    DEFAULT_SRV_ID              = 1

    CLIENT_ID_DICT_KEY          = "SRC"
    METHOD_DICT_KEY             = "METHOD"
    ARGS_DICT_KEY               = "ARGS"
    RESPONSE_DICT_KEY           = "RESPONSE"

    @staticmethod
    def GetServerRPCTopic(idNumber=1):
        """@brief Responsible for getting the Server RPC topic string.
           @param idNumber The idNumber of the RPC server that RPC messages can be sent to.
           @return A string that represents the RPC server topic."""
        return "server%d/RPC" % (idNumber)

    @staticmethod
    def GetClientID(id=1):
        """@brief Responsible for getting a client ID string.
           @param id The unique id of the MQTT client.
           @return A string that represents the unique client ID."""
        return "client%s/RPC" % ( str(id) )

    def __init__(self, uo, options):
        """@brief Responsible fopr providing RPC functionality via an MQTT server.
           @param uo A UO instance that implements the info(text) and error(text) methods
                       to send information to the user.
           @param options An options instance.
                    options.sid = A number to uniquely identify the server
                    options.cid = A number to uniquely identify the client
                    options.server = The host address of the MQTT server
                    options.port = The port number to connect to the MQTT server
                    options.keepalive = The keepalive period in seconds

           The MQTTRPCClient class can only be a base class and should be extended. Child classes must
           implement/override the _onMessage() method."""
        self._uo = uo
        self._options = options

        self._serverRPCTopic = MQTTRPCClient.GetServerRPCTopic(idNumber=self._options.sid)

        self._client = mqtt.Client()
        self._client.on_connect = self._onConnect
        self._client.on_message = self._onMessage

    def connect(self):
        """@brief Connect to the MQTT server"""
        self._client.connect(self._options.server, self._options.port, self._options.keepalive)

    def loopForever(self):
        """@brief Wait here to service messages after a successfll connection."""
        self._client.loop_forever()

    def _onConnect(self, client, userdata, flags, rc):
        """@brief Called when connected to the MQTT server."""
        self._client.subscribe( self._serverRPCTopic )
        self._uo.info("Connected to MQTT server (%s:%d) and subscribed to %s" % (self._options.server, self._options.port, self._serverRPCTopic) )

    @abstractmethod
    def _onMessage(self, client, userdata, msg):
        """@brief Called when a message is received from the MQTT server.
                  This method mst be implented in a child class."""
        pass

class MQTTRPCProviderClient(MQTTRPCClient):

    def __init__(self, uo, options, rpcMethodProviderList):
        """@brief Responsible for providing RPC functionality via an MQTT server.
                  MQTTRPCProviderClient instances implement the RPC at the destination/remote side
                  and return the results to the caller side.
           @param uo A UO instance that implements the info(text) and error(text) methods
                     to send information to the user.
           @param options An options instance.
                    options.sid = A number to uniquely identify the server
                    options.cid = A number to uniquely identify the client receiving responses from the server.
                    options.server = The host address of the MQTT server
                    options.port = The port number to connect to the MQTT server
                    options.keepalive = The keepalive period in seconds
           @param rpcMethodProviderList A list/tuple of class instances that provide the RPC methods."""
        MQTTRPCClient.__init__(self, uo, options)
        self._rpcMethodProviderList=rpcMethodProviderList

    def _onMessage(self, client, userdata, msg):
        """@brief Called when a message is received from the MQTT server.
           @param client:     the client instance for this callback
           @param userdata:   the private user data as set in Client() or userdata_set()
           @param message:    an instance of MQTTMessage.
                              This is a class with members topic, payload, qos, retain."""
        try:

          rxStr = msg.payload.decode()
          self._uo.info( "RX: %s" % (rxStr) )

          jsonDict = json.loads( msg.payload.decode() )

          if MQTTRPCClient.CLIENT_ID_DICT_KEY in jsonDict and MQTTRPCClient.METHOD_DICT_KEY in jsonDict:
              clientID = jsonDict[MQTTRPCClient.CLIENT_ID_DICT_KEY]
              methodName = jsonDict[MQTTRPCClient.METHOD_DICT_KEY]
              args = jsonDict[MQTTRPCClient.ARGS_DICT_KEY]

              method = None
              for rpcMethodProvider in self._rpcMethodProviderList:
                  if hasattr(rpcMethodProvider, methodName):
                      method = getattr(rpcMethodProvider, methodName)

              if method:
                  if len(args) > 0:
                      response = method(args)
                  else:
                      response = method()

                  jsonDict[MQTTRPCClient.RESPONSE_DICT_KEY]=response

                  jsonString = json.dumps(jsonDict)

                  self._uo.info( "TX: %s" % (jsonString) )
                  client.publish(clientID, jsonString)

              else:
                  raise AttributeError("Unable to find a provider of the %s method." % (methodName) )

        except:
            tb = traceback.format_exc()
            self._uo.error(tb)



class MQTTRPCCallerClient(MQTTRPCClient):

    def __init__(self, uo, options, responseTimeoutSeconds = 10):
        """@brief Responsible fopr providing RPC functionality via an MQTT server.
                  MQTTRPCCallerClient instances implement the RPC at the src/caller side
                  sending RPC requests to destination/remote and reciving responses.
           @param uo A UO instance that implements the info(text) and error(text) methods
                     to send information to the user.
           @param options An options instance.
                    options.sid = A number to uniquely identify the server responding to RPC calls.
                    options.cid = A number to uniquely identify the client receiving responses from the server.
                    options.server = The host address of the MQTT server
                    options.port = The port number to connect to the MQTT server
                    options.keepalive = The keepalive period in seconds
           @param timeoutSeconds The number of seconds to wait for a timeout when no response is received."""
        MQTTRPCClient.__init__(self, uo, options)
        self._responseTimeoutSeconds = responseTimeoutSeconds

        self._clientSRC = MQTTRPCClient.GetClientID(options.cid)

        self._serverRPCTopic = MQTTRPCClient.GetServerRPCTopic(idNumber=self._options.sid)

        self._sendMsgDict = None
        self._responseQueue = Queue()

        self._condition = Condition()

    def _onMessage(self, client, userdata, msg):
        """@brief Called when a message is received from the MQTT server.
           @param client:     the client instance for this callback
           @param userdata:   the private user data as set in Client() or userdata_set()
           @param message:    an instance of MQTTMessage.
                              This is a class with members topic, payload, qos, retain.
           @return None"""
        try:

          responseDict = json.loads( msg.payload.decode() )
          if responseDict and MQTTRPCClient.RESPONSE_DICT_KEY in responseDict:
              self._condition.acquire()
              self._responseQueue.put(responseDict[MQTTRPCClient.RESPONSE_DICT_KEY])
              self._condition.notify()
              self._condition.release()

        except:
            tb = traceback.format_exc()
            self._uo.error(tb)

    def _getResponse(self):
        """@brief Internal method used to get the response to an RPC
           @return The response to the RPC or None if a timeout occurs."""

        # blocks until the response is processed or a timeout occurs
        self._condition.wait(timeout=self._responseTimeoutSeconds)

        response = None
        if not self._responseQueue.empty():
            response = self._responseQueue.get()

        return response

    def _getRPCString(self):
        """@brief Get the last RPC called as a string.
           @return The RPC string representation."""
        if self._sendMsgDict and MQTTRPCClient.METHOD_DICT_KEY in self._sendMsgDict and MQTTRPCClient.ARGS_DICT_KEY in self._sendMsgDict:
            return "%s(%s)" % (self._sendMsgDict[MQTTRPCClient.METHOD_DICT_KEY], self._sendMsgDict[MQTTRPCClient.ARGS_DICT_KEY])
        else:
            return ""

    def rpcCall(self, methodName, argList):
        """@brief Call an RPC
           @param methodName The name of the RPC to call. Currently this is just the method name.
                             This method could exist on an instance of any object. We could have
                             made this include instance details but to keep things simple
                             just the method name is provided.
           @param argList The arguments for the RPC
           @return The response to the RPC."""
        self._sendMsgDict={}
        self._sendMsgDict[MQTTRPCClient.CLIENT_ID_DICT_KEY]=self._clientSRC
        self._sendMsgDict[MQTTRPCClient.METHOD_DICT_KEY]=methodName
        self._sendMsgDict[MQTTRPCClient.ARGS_DICT_KEY]=argList

        jsonDict = json.dumps(self._sendMsgDict, indent=4, sort_keys=True)

        self._client.subscribe(self._clientSRC)

        self._condition.acquire()

        response = None
        try:
            self._client.publish(self._serverRPCTopic, jsonDict)

            response = self._getResponse()

        finally:

            self._condition.release()

        return response
