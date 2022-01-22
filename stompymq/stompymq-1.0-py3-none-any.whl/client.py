from .frame import STOMPFrame, STOMPStream, STOMPError, AckMode
from socket import socket, AF_INET, SOCK_STREAM
from .util import to_str, to_bytes

class STOMPSubscription(object):
    
    def __init__(self, client, id, dest, ack_mode, send_acks):
        self.ID = id
        self.Destination = dest
        self.AckMode = ack_mode
        self.Client = client
        self.SendAcks = send_acks
        
    def cancel(self):
        self.Client.unsubscribe(self.ID)
        self.Client = None
        
class STOMPTransaction(object):
    
    def __init__(self, client, txn_id):
        self.ID = txn_id
        self.Client = client
        self.Closed = False
        
    def send(self, command, **args):
        if self.Closed:
            raise STOMPError("Transaction already closed")
        return self.Client.send(command, transaction=self.ID, **args)
        
    def message(self, *params, **args):
        if self.Closed:
            raise STOMPError("Transaction already closed")
        return self.Client.message(*params, transaction=self.ID, **args)
        
    def recv(self):
        if self.Closed:
            raise STOMPError("Transaction already closed")
        return self.Client.recv(transaction=self.ID)
        
    def commit(self, **args):
        if self.Closed:
            raise STOMPError("Transaction already closed")
        out = self.Client.send("COMMIT", transaction=self.ID, **args)
        self.Closed = True
        return out
        
    def abort(self, **args):
        if self.Closed:
            raise STOMPError("Transaction already closed")
        out = self.Client.send("ABORT", transaction=self.ID, **args)
        self.Closed = True
        return out

    def nack(self, ack_id):
        if self.Closed:
            raise STOMPError("Transaction already closed")
        return self.Client.nack(ack_id, transaction=self.ID)

    def ack(self, ack_id, transaction=None):
        if self.Closed:
            raise STOMPError("Transaction already closed")
        return self.Client.ack(ack_id, transaction=self.ID)

        
class STOMPClient(object):
    
    ProtocolVersion = "1.2"         # the only supported version
    
    def __init__(self):
        """
        STOMPClient constructor does not have any arguments.
        """
        self.Sock = None
        self.BrokerAddress = None
        self.Connected = False
        self.Stream = None
        self.NextID = 1
        self.Subscriptions = {}         # id -> subscription
        self.Callbacks = []
        
    def next_id(self, prefix=""):
        out = self.NextID
        self.NextID += 1
        if prefix: prefix = prefix + "."
        return f"{prefix}{out}"
        
    def connect(self, addr_list, login=None, passcode=None, headers={}, **kv_headers):
        """
        Connects to a broker. On successfull connection, sets the following attributes:
        
        client.BrokerAddress - tuple (ip_address, port) - actual address of the broker the connection was established to
        clint.Connected = True
        
        :param addr_list: a single broker address as tuple (ip_address, port), or a list of tuples - addresses
        :param str login: login id to use, default: None
        :param str passcode: pass code to use, default: None
        :param dict headers: additional headers for the CONNECT frame, default: none
        :param kv_headers: additional headers for the CONNECT frame
        :return: CONNECTED frame returned by the broker
        """
        if self.Connected:
            raise RuntimeError("Already connected")
            
        if not isinstance(addr_list, list):
            addr_list = [addr_list]
            
        last_error = None
        response = None
        broker_addr = None
        for addr in addr_list:
            sock = socket(AF_INET, SOCK_STREAM)
            try:    sock.connect(addr)
            except: continue
            
            stream = STOMPStream(sock)
            
            headers = {"accept-version":self.ProtocolVersion}
            if login is not None:   headers["login"] = login
            if passcode is not None:   headers["passcode"] = passcode
            frame = STOMPFrame("CONNECT", headers=headers)
            stream.send(frame)
            response = stream.recv()
            if response.Command == "ERROR":
                last_error = STOMPError(response.get("message", ""), response.Body)
            elif response.Command != "CONNECTED":
                last_error = STOMPError(f"Error connecting to the broker. Unknown response command: {response.Command}",
                    response)
            else:
                self.Connected = True
                self.Stream = stream
                self.Sock = sock
                self.BrokerAddress = addr
                break
        if not self.Connected:
            if last_error:  raise last_error
            else:   raise RuntimeError("Failed to connect to a broker")
        return response        

    def add_callback(self, cb):
        """
        Add callback object to receive out-of band messages while waiting for a receipt
        
        :param object cb: - callback object        
        """
        self.remove_callback(cb)
        self.Callbacks.append(cb)
        
    def remove_callback(self, cb=None):
        """
        Remove a single callback object or all callback objects
        
        :param object cb: - callback object or None. If None, all callback objects will be removed
        """
        
        if cb is None:
            self.Callbacks = []
        else:
            try:    self.Callbacks.remove(cb)
            except: pass

    def subscribe(self, dest, ack_mode="auto", send_acks=True):
        """
        Subscribe to messages sent to the specified destination
        
        :param str dest: destination
        :param str ack_mode: can be either "auto" (default), "client" or "client-individual"
        :param boolean send_acks: whether the client should automatically send ACKs received on this scubscription
        :return: subscription id
        :rtype: str
        """
        if not isinstance(ack_mode, AckMode):
            ack_mode = AckMode(ack_mode)
        subscription = STOMPSubscription(self, self.next_id("s"), dest, ack_mode, send_acks)
        receipt = self.send("SUBSCRIBE", headers={
            "destination":dest,
            "ack":ack_mode.value,
            "id":subscription.ID
        }, receipt=True)
        self.Subscriptions[subscription.ID] = subscription
        return subscription.ID

    def unsubscribe(self, sub_id):
        """
        Remove subscription
        
        :param str sub_id: subscription id
        """
        subscription = self.Subscriptions.pop(sub_id, None)
        if subscription is not None:
            receipt = self.send("UNSUBSCRIBE", id=sub_id, receipt=True)

    def send(self, command, headers={}, body=b"", transaction=None, receipt=False, wait=True, **kv_headers):
        """
        Send the frame
        
        :param str command: frame command
        :param dict headers: frame headers, default - {}
        :param bytes body: frame body, default - empty body
        :param str or boolean receipt: if True or non-empty string, the frame will include "receipt" header.
            If receipt is a str, it will be used as is.
            If receipt=True, the client will generate new receipt id.
            If receipt=False, do not require a receipt.
        :param kv_headers: additional headers to add to the frame
        :returns: the receipt id used or None
        :rtype: str
        """
        h = {}
        h.update(headers)
        h.update(kv_headers)
        if receipt == True:
            receipt = self.next_id("r")
        if receipt:
            h["receipt"] = receipt
        frame = STOMPFrame(command, headers=h, body=to_bytes(body))
        self.Stream.send(frame)
        if receipt and wait:
            return self.wait_for_receipt(receipt, transaction=transaction)
        else:
            return receipt
        
    def wait_for_receipt(self, receipt, transaction=None):
        """
        Wait for a receipt for a previously sent frame. Frames received while waiting for the receipt will be
        sent to the callbacks added to the client.
        
        :param str receipt: the receipt id to wait for
        :param str or None transaction: transaction id to associate the frame with, or None
        :return: the "receipt" frame received or None if the connection was closed before the receipt was received
        :rtype: STOMPFrame
        """
        frame = self.recv(transaction)
        while frame is not None:
            if frame.Command == "RECEIPT" and frame["receipt-id"] == receipt:
                return frame
            self.callbacks(frame)
            frame = self.recv(transaction)
        return None     # closed

    def message(self, destination, body=b"", id=None, headers={}, receipt=False, wait=True,
                    transaction=None, **kv_headers):
        """
        Conventience method to send a message. Uses send().

        :param str destination: destination to send the message to
        :param bytes body: message body, default - empty
        :param str or None id: add message-id header, if not None
        :param dict headers: headers to add to the message, default - empty
        :param boolean or str receipt: if True or non-empty string, the frame will include "receipt" header.
            If ``receipt`` is a str, it will be used as is.
            If ``receipt`` is True, the client will generate new receipt id.
            If ``receipt`` is False, do not require a receipt.
        :param boolean wait: whether to wait for the recepit to be returned, default=True. Ignored if ``receipt`` is False.
        :param str transaction: transaction id to associate the frame with, or None
        :return: If receipt was False, then None.
            If ``wait`` was False, return receipt id for the message sent.
            If ``wait`` was True or non-empty str, wait for the receipt and return None if the connection was closed or
            the received "receipt" frame
        """
        headers = {}
        if id is not None:
            headers["message-id"] = id
        return self.send("SEND", headers=headers, body=body, destination=destination, 
                receipt=receipt, transaction=transaction, wait=wait, **kv_headers)

    def callback(self, frame):
        method = "on_" + frame.Command.lower()
        for cb in self.Callbacks:
            try:    method = getattr(cb, method)
            except: pass
            else:   
                if method(self, frame) == "stop":
                    break

    def recv(self, transaction=None):
        """
        Receive next frame
        
        :param str or None transaction: transaction to associate the automatically sent ACK, or None
        :return: frame received or None, if the connection was closed
        :rtype: STOMPFrame or None
        """
        frame = self.Stream.recv()
        if frame is None:
            # EOF
            self.close()
            return None
            
        if frame.Command == "MESSAGE" and "ack" in frame:
            sub_id = frame["subscription"]
            subscription = self.Subscriptions.get(sub_id)
            if subscription is None or subscription.SendAcks:
                self.ack(frame["ack"], transaction)
        return frame
        
    def nack(self, ack_id, transaction=None):
        """
        Send NACK frame
        
        :param str ack_id: NACK id to send
        :param str or None transaction: transaction id to associate the NACK with, default: None
        """
        headers = {"id":ack_id}
        if transaction is not None:
            headers["transaction"] = transaction
        self.send("NACK", headers)

    def ack(self, ack_id, transaction=None):
        """
        Send ACK frame
        
        :param str ack_id: NACK id to send
        :param str or None transaction: transaction id to associate the ACK with, default: None
        """
        headers = {"id":ack_id}
        if transaction is not None:
            headers["transaction"] = transaction
        self.send("ACK", headers)

    def transaction(self, txn_id=None):
        """
        Creates and begins new transaction
        
        :param str or None txn_id: transaction ID or None (default), in which case a new transaction ID will be generated
        """
        txn_id = txn_id or self.next_id("t")
        self.send("BEGIN", transaction=txn_id, receipt=True)
        return STOMPTransaction(self, txn_id)

    def disconnect(self):
        """
        Send DISCONNECT frame, wait for receipt and close the connection.
        """
        if self.Connected:
            receipt = self.send("DISCONNECT", receipt=True)
            self.wait_for_receipt(receipt)
            self.close()

    def close(self):
        if self.Connected:
            self.Sock.close()
            self.Sock = None
            self.Callbacks = None
            self.Subscriptions = None
            self.Connected = False
        
    def __del__(self):
        self.disconnect()

    def __iter__(self):
        """
        The client can be used as an iterator, returning next received frame on every iteration. The iteration stops
        when the connection closes:
        
            client = STOMPClient()
            client.connect(...)
            for frame in client:
                ...
            # connection closed

        """
        return MessageIterator(self)

class MessageIterator(object):

    def __init__(self, client):
        self.Client = client
        
    def __next__(self):
        frame = self.Client.recv()
        if frame is None:
            raise StopIteration()
        return frame
        
def connect(addr_list, login=None, passcode=None, headers={}):
    """
    Creates the client object and connects it to the Broker
    
    :param addr_list: a single broker address as tuple (ip_address, port), or a list of tuples - addresses
    :param str login: login id to use, default: None
    :param str passcode: pass code to use, default: None
    :param dict headers: additional headers for the CONNECT frame, default: none
    :return: STOMPlient instance connected to the Broker
    :rtype: STOMPClient    
    """
    client = STOMPClient()
    client.connect(addr_list, login=login, passcode=passcode, headers=headers)
    return client

