import _thread
import os
import socket
import threading
import time
from pyngrok import ngrok
from .utils import *

class _ClientOOP():
    def __init__(self, ip, conn, console_output:bool=True, **kwargs):
        self._ip = ip
        self.conn = conn

        self._data = kwargs.get("data", {})
        self.timeout = kwargs.get("timeout", None)

        self.console_output = console_output

        self.conn.settimeout(self.timeout)
    
    @property
    def ip(self):
        return self._ip
    
    @property
    def data(self):
        return self._data
    
    @property
    def manager(self):
        return self.conn

    @property
    def is_connected(self):
        return self.check_connection()

    def set_data(self, data):
        self._data = data

    def set(self, var_before:str, var_after:str):
        eval(f"{var_before} = {var_after}")

    def send(self, msg, method:SEND_METHOD=SEND_METHOD.default_send):
        self.check_connection()

        time.sleep(0.2)
        def _send(msg, method):
            if isinstance(msg, str):
                msg = msg.encode()
            elif isinstance(msg, bytes):
                pass
            else:
                msg = str(msg).encode()

            if self.console_output: outstr("DEBUG", f"Send to {self.ip}: {msg.decode()}")

            if method == 0:
                self.conn.send(str(len(msg)).encode())
                time.sleep(0.5)
                self.conn.send(msg)
            elif method == 1:
                self.conn.send(msg)
            else:
                raise Exception(f"Unknown method -> {method}")
        
        try:
            _send(msg, method)
            return 200, None
        except ConnectionAbortedError as e:
            return 500, e

        except socket.timeout as e:
            return 500, e

        except ConnectionResetError as e:
            return 500, e
    
        except OSError as e:
            return 500, e
    
        except WindowsError as e:
            return 500, e

        except Exception as e:
            raise e
    
    def recv(self, buffer:int=2048):
        self.check_connection()

        def _recv(buffer):
            received = self.conn.recv(buffer).decode()

            try:
                bfsize = int(received)
            except Exception as e:
                msg = str(received)
                if self.console_output: outstr("DEBUG", f"Recv from {self.ip}: {received}")
                return msg

            received_chunks = []
            remaining = bfsize
            while remaining > 0:
                if remaining > 10000:
                    received = self.conn.recv(10000).decode()
                else:
                    received = self.conn.recv(remaining).decode()
                if not received:
                    raise Exception(f'{self.ip} Error: unexpected EOF')
                received_chunks.append(received)
                remaining -= len(received)

            outp = ''.join(received_chunks)
            if self.console_output: outstr("DEBUG", f"Recv from {self.ip}: {outp}")
            return str(outp)

        try:
            return response_class(200, _recv(buffer), None)

        except ConnectionAbortedError as e:
            return response_class(500, None, e)

        except ConnectionResetError as e:
            return response_class(500, None, e)
    
        except OSError as e:
            return response_class(500, None, e)
    
        except WindowsError as e:
            return response_class(500, None, e)

        except socket.timeout as e:
            return response_class(500, None, e)

        except Exception as e:
            raise e
    
    def check_connection(self):
        if not self._check_connection():
            try:
                self.conn.settimeout(self.timeout)
            except OSError:
                self.conn.close()
                return False
            self.conn.close()
            return False

        try:
            self.conn.settimeout(self.timeout)
        except OSError:
            self.conn.close()
            return False
        return True
    
    def _check_connection(self):
        try:
            self.conn.settimeout(1.4)
            self.conn.recv(16, socket.MSG_PEEK)
            return True

        except BlockingIOError:
            return True 

        except ConnectionResetError:
            return False

        except socket.timeout:
            return True
        
        except WindowsError:
            return False
        
        except OSError:
            return False

        except Exception as e:
            outstr("ERROR", str(e))

class Server():
    def __init__(
        self,
        ip,
        port:int, 
        console_output:bool=True,
        client_timeout:int=None,
        timeout:int=None,
        use_pyngrok:bool = False,
        pyngrok_options:dict = {},
        **kwargs
    ):
        self.use_pyngrok = use_pyngrok
        self.pyngrok_options = pyngrok_options

        if ip == "auto":
            self.IP = socket.gethostbyname(socket.gethostname()) 
        else:
            self.IP = ip

        self.PORT = port
        self.console_output = console_output
        self.client_timeout = client_timeout
        self.timeout = timeout

        self.decorator_functions_call = []
        self.decorator_client_disconnect = []

        self.clients = []

    def start(self):
        if self.console_output: outstr("INFO", "Starting server...")
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.server.bind((self.IP, self.PORT))
        self.server.listen(1)
        self.server.settimeout(self.timeout)
        
        if self.use_pyngrok: self.PUBLIC_URL = ngrok.connect(self.PORT, self.pyngrok_options.get("mode", "tcp"), options={"remote_addr": "{}:{}".format(self.IP, self.PORT)})

        if self.console_output:
            try:
                if self.console_output: outstr("INFO", "Server Address: " + str(self.PUBLIC_URL).split("")[1])
            except:
                if self.console_output: outstr("INFO", f"Server Address: {self.IP}:{self.PORT}")

            if self.console_output: outstr("INFO", "Listening for incoming connections...")
        
        threading.Thread(target=self.check_clients).start()
        threading.Thread(target=self._accept).start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            for client in self.clients:
                client.send("exit")

            outstr("info", "KeyboardInterrupt. Exiting...")
            os._exit(0)
        
    def _accept(self):
        while True:
            conn, addr = self.server.accept()
            if self.console_output: outstr("ACCESS", f"Connection from {addr} has been established!", start="\n")

            new_client = _ClientOOP(ip=addr, conn=conn, console_output=self.console_output, timeout=self.client_timeout)
            self.clients.append(new_client)

            for func in self.decorator_functions_call:
                _thread.start_new_thread(func, (new_client,))
    
    def check_clients(self):
        def _check(client):
            if not client.check_connection():
                self.clients.remove(client)
                if self.console_output: outstr("DEBUG", f"{client.ip} is no longer connected.")
                for func in self.decorator_client_disconnect:
                    _thread.start_new_thread(func, (client,))

        while True:
            time.sleep(10)
            for client in self.clients:
                _thread.start_new_thread(_check, (client,))
    
    def shutdown(self):
        if self.console_output: outstr("INFO", f"Shutdown server.")
        for client in self.clients:
            client.send('exit')

        ngrok.kill()
        os._exit(1)

    @property
    def ip(self):
        return self.IP
    
    @property
    def ngrok_url(self):
        return self.PUBLIC_URL
    
    @property
    def connected_clients(self):
        return self.clients
    
    @property
    def socket_object(self):
        return self.server

    def sendall(self, msg):
        if isinstance(msg, str):
            msg = msg.encode()
        elif isinstance(msg, bytes):
            pass
        else:
            msg = str(msg).encode()

        self.server.sendall(msg)
    
    def on_client_connect(self, *args, **kwargs):
        def decorator(func):
            if func not in self.decorator_functions_call:
                self.decorator_functions_call.append(func)
            return func

        return decorator
    
    def on_client_disconnect(self, *args, **kwargs):
        def decorator(func):
            if func not in self.decorator_client_disconnect:
                self.decorator_client_disconnect.append(func)
            return func

        return decorator
