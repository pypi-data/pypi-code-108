""" Proxy into Sermos Cloud hosted services.

    Thank you to the following great resources:
        https://realpython.com/python-sockets/
        https://gist.github.com/WangYihang/e7d36b744557e4673d2157499f6c6b5e
"""
import socket
import threading
import logging
import json

from sermos.cloud import SermosCloud
from sermos.constants import DEPLOYMENTS_SERVICE_URL, PROXY_SERVICE_URL

logger = logging.getLogger(__name__)
PROXY_HEADER_BYTES = 4


class TunnelError(Exception):
    pass


class ProxyError(Exception):
    pass


class ProxyBase:
    """ Base class with common Proxy functions
    """
    def _close_conn(self, conn: socket.socket):
        """ Close and cleanup a socket connection
        """
        try:
            conn_name = conn.getsockname()
            addr = conn_name[0]
            port = conn_name[1]
            no = conn.fileno()
            logger.info(f"[-] Closing connecion! {addr}:{port} [{no}]")
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
        except OSError as e:
            if e.errno == 9 or e.errno == 57:
                pass
            else:
                logger.error(
                    f"[x] Error: socket.close() exception for {addr}:\n"
                    f"{repr(e)}")
        finally:
            conn = None  # Delete reference to socket obj for garbage collection


class PortForwarder(ProxyBase):
    """ Port forwarding from remote service to locally bound port.
    """
    def _handle(self, buffer):
        return buffer

    def transfer(self, src: socket.socket, dst: socket.socket, data_out: bool):
        """ Read (recv) data from `src` and send to `dst`
        """
        try:
            src_name = src.getsockname()
            src_address = src_name[0]
            src_port = src_name[1]
        except OSError as e:
            # 9 == Bad file descriptor
            # 57 == Socket is not connected
            if e.errno == 9 or e.errno == 57:
                logger.debug(f"Unable to get details for src: {src}")
                return
            raise e  # Raise if unknown error type
        try:
            dst_name = dst.getsockname()
            dst_address = dst_name[0]
            dst_port = dst_name[1]
        except OSError as e:
            # 9 == Bad file descriptor
            # 57 == Socket is not connected
            if e.errno == 9 or e.errno == 57:
                logger.debug(f"Unable to get details for dst: {dst}")
                return
            raise e  # Raise if unknown error type

        while True:
            try:
                buffer = src.recv(1024)
            except Exception as e:
                logger.debug(f"\nsrc: {src_address}:{src_port}\n"
                             f"dst: {dst_address}:{dst_port}\n"
                             f"src.recv exception: {e}")
                break

            if len(buffer) == 0:
                logger.debug(f"Read b'' from {dst} ...\n"
                             f"Closing [{dst_address}:{dst_port}]...")
                self._close_conn(dst)
                break

            # Helpful debugging logs
            if data_out:
                logger.debug(f"{src_address}:{src_port} >>> "
                             f"{dst_address}:{dst_port} [{len(buffer)}]")
            else:
                logger.debug(f"{dst_address}:{dst_port} <<< "
                             f"{src_address}:{src_port} [{len(buffer)}]")
            try:
                dst.send(self._handle(buffer))
            except socket.error:
                logger.debug(f"Socket error on send to {dst}; closing ...")
                self._close_conn(dst)
            except Exception as e:
                logger.debug(f"dst.send exception: {e}")
                break

    def remote_tunnel(self, src_socket: socket.socket,
                      dst_socket: socket.socket):
        """ Initialize a tunnel between source and destination hosts
        """

        logger.info("[.] Tunnel connecting ...")

        # src  == remote proxy server
        # dst == local client socket
        s = threading.Thread(target=self.transfer,
                             args=(src_socket, dst_socket, False))
        r = threading.Thread(target=self.transfer,
                             args=(dst_socket, src_socket, True))

        s.start()
        r.start()

        if s.is_alive() and r.is_alive():
            logger.info("[+] Tunnel connected!")
        else:

            msg = f"[x] Tunnel failed:\n" +\
                  f"src: {s.is_alive()}\ndst: {r.is_alive()}"
            raise TunnelError(msg)


class SermosLocalProxyClient(ProxyBase):
    """ An individual local client connected to our local proxy (e.g. recis-cli)
    """
    def __init__(self, remote_host: str, remote_port: int,
                 tunnel_payload: dict):
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.tunnel_payload = tunnel_payload
        self.remote_server_socket = None

    def connect(self):
        """ Connect to our 'remote host' (the Proxy Service deployed in a
            Sermos Cloud deployment).
        """
        # Do initialization handshake here first. If that's successful,
        # go into tunnel + transfer mode.
        logger.info(f"[.] Attempting to connect to remote Proxy Service "
                    f"{self.remote_host}:{self.remote_port} ...")

        try:
            self.remote_server_socket = socket.socket(socket.AF_INET,
                                                      socket.SOCK_STREAM)
            self.remote_server_socket.connect(
                (self.remote_host, self.remote_port))
        except ConnectionRefusedError:
            raise ProxyError(
                f"[x] Unable to connect to {self.remote_host}:{self.remote_port}"
                f" ... Connection Refused ...")
        except Exception as e:
            raise ProxyError(f"[x] Unknown exception occurred: {e}")

        # Send tunnel payload to verify we can establish connection
        # tunnel_payload['jwt'] = tunnel_payload['jwt'] + 'foo'  # Testing
        msg = json.dumps(self.tunnel_payload).encode('utf-8')

        # First, tell remote length of following message that includes
        # jwt and other config details
        header = (len(msg)).to_bytes(PROXY_HEADER_BYTES, byteorder='big')
        self.remote_server_socket.send(header)

        # Second, send jwt + config details in the payload
        self.remote_server_socket.send(msg)

        # Sermos Cloud Proxy will send a single byte 0/1 to indicate
        # bad/good state.
        connected = self.remote_server_socket.recv(1)
        if int(connected.decode('utf-8')) == 0:
            self._close_conn(self.remote_server_socket)
            raise ProxyError("[x] Invalid request made. Connection closed ...")

        logger.info(f"[+] Proxy connection established to "
                    f"{self.remote_host}:{self.remote_port} "
                    f"[{self.remote_server_socket.fileno()}]")

    def start(self, client_socket: socket.socket):
        """
        """
        pf = PortForwarder()
        pf.remote_tunnel(self.remote_server_socket, client_socket)


class SermosProxy(SermosCloud, ProxyBase):
    """ Primary Sermos Deployment class for invocation and status updates.
    """
    def __init__(self,
                 proxy_id: str,
                 service_id: str,
                 local_port: int,
                 local_host: str = '127.0.0.1',
                 max_connection: int = 16,
                 deployment_id: str = None,
                 access_key: str = None,
                 base_url: str = None,
                 debug: bool = False):
        """ Arguments:
                proxy_id: Proxy Service ID (adj-noun-12345). Find in your
                    Sermos Cloud Console.
                service_id: Service ID (adj-noun-12345). Find in your
                    Sermos Cloud Console.
                local_port: Local port on which to bind.
                local_host: Local host ip on which to bind.
                max_connection: Maximum connections the port forwarder accepts.
                deployment_id (optional): UUID for Deployment. Find in your Sermos
                    Cloud Console. If not provided, looks in environment under
                    `SERMOS_DEPLOYMENT_ID`
                access_key (optional): Access key, issued by Sermos, that
                    dictates the environment into which this request will be
                    deployed. Defaults to checking the environment for
                    `SERMOS_ACCESS_KEY`. If not found, will exit.
                base_url (optional): Defaults to primary Sermos Cloud base URL.
                    Only modify this if there is a specific, known reason to do so.
                debug (optional): Rarely use - this is for local development only.
        """
        super().__init__(access_key, base_url, deployment_id)
        self.proxy_id = proxy_id  # ID for the Proxy Service
        self.service_id = service_id  # ID for the target Service
        self.local_port = local_port  # Local port to bind to
        self.local_host = local_host  # Local host to bind to
        self.max_connection = max_connection  # Default is typically fine
        self.debug = debug

        # Dynamic variables based on call to Sermos Cloud for target service
        self.service_url = DEPLOYMENTS_SERVICE_URL.format(
            self.base_url, self.deployment_id, self.service_id)
        self.service_internal_id = None  # Set internally
        self.service_hostname = None
        self.k8s_service_port = None
        self.k8s_service_id = None

        # Dynamic variables based on call to Sermos Cloud for proxy service
        self.proxy_url = DEPLOYMENTS_SERVICE_URL.format(
            self.base_url, self.deployment_id, self.proxy_id)
        self.proxy_port = None
        self.proxy_hostname = None

        # Signed data from Sermos Cloud, sent to Proxy Service
        self.proxy_data = None  # Unsigned data from server
        self.proxy_token = None  # Data inside signed jwt

    def _get_service_info(self):
        """ Get details about this service.
        """
        service = self.get(self.service_url, as_dict=True)
        if not service.get('data'):
            msg = f"Unable to find service with ID `{self.service_id}`\n"\
                  f"Ensure you have the correct access key, deployment id, "\
                  f"and service id as found in your Sermos Cloud console."
            raise ValueError(msg)
        data = service.get('data', {})
        self.service_internal_id = data.get('id')
        conn_settings = data.get('connectionSettings', {})

        self.service_hostname = conn_settings['hostname']['value']

    def _get_jwt(self):
        """ Ask Sermos Cloud for a JWT to use for the proxy request.
        """
        proxy_url = PROXY_SERVICE_URL.format(self.base_url, self.deployment_id,
                                             self.service_internal_id)
        token_data = self.get(proxy_url, as_dict=True)
        if not token_data.get('data'):
            msg = f"Unable to retrieve proxy token for service ID "\
                  f"`{self.service_id}` in deployment {self.deployment_id}.\n"\
                  f"Request was made to {self.base_url}\n"\
                  f"Ensure you have the correct access key, deployment id, "\
                  f"and service id as found in your Sermos Cloud console."
            raise ValueError(msg)

        # Raw data sent as a convenience so Sermos library does not need to
        # include ability to unpack JWT contents. Signed JWT used to send
        # request to Proxy Service and contains the same data, just signed.
        self.proxy_data = token_data['data']['raw']
        self.proxy_token = token_data['data']['jwt']

    def _determine_service_port(self, auto_select: bool = False):
        """ Services that are available to this proxy will have one or more
            services with exposed ports. If only one available, just select
            and move on. If > 1, ask user which to select. This is relevant
            for services such as HA database deployments that have
            primary/replica sets, for example.

            Example k8s metadata structure:
                'k8s_metadata': {
                    'hostname': 'vast-duck-1b525f.sermosapp.com',
                    'vast-duck-1b525f-headless': {
                        ...
                        'ports': [
                            {
                                ...
                                'port': 6379
                            }
                        ]
                    },
                    {...}
                }

            Example available_svcs structure:
                {
                    1: ['vast-duck-1b525f-headless', [6379]],
                    2: ...
                }

        """
        available_svcs = {}
        svc_count = 1  # Start at 1 for human readability on svc selection
        for idx, svc in enumerate(self.proxy_data['k8s_metadata']):
            if type(self.proxy_data['k8s_metadata'][svc]) != dict:
                continue
            available_svcs[svc_count] = [svc, []]
            for port in self.proxy_data['k8s_metadata'][svc]['ports']:
                available_svcs[svc_count][1].append(port['port'])
            svc_count += 1

        if auto_select:
            self.k8s_service_id = self.service_hostname
            self.k8s_service_port = available_svcs[1][1][0]
        else:
            # User prompt to select the Service
            msg = "\nChoose the service to which to connect:\n\n"
            for svc_idx in available_svcs:
                msg += f"    {svc_idx}: {available_svcs[svc_idx][0]}\n"
            msg += "\n> "
            svc_selected = int(input(msg))
            if svc_selected not in available_svcs:
                raise ValueError("Invalid selection ...")
            self.k8s_service_id = available_svcs[svc_selected][0]

            # User prompt to select the Port
            msg = "\nChoose the service port to use:\n\n"
            idx = 1
            for port in available_svcs[svc_selected][1]:
                msg += f"    {idx}: {port}\n"
                idx += 1
            msg += "\n> "
            sel_port = int(input(msg))
            if len(available_svcs[svc_selected][1]) < sel_port or len(
                    available_svcs[svc_selected][1]) > sel_port:
                raise ValueError("Invalid selection ...")
            self.k8s_service_port = available_svcs[svc_selected][1][sel_port -
                                                                    1]

    def _get_proxy_info(self):
        """ Get details about the Proxy Service.
        """
        proxy = self.get(self.proxy_url, as_dict=True)
        if not proxy.get('data'):
            msg = f"Unable to find proxy with ID `{self.proxy_id}`\n"\
                  f"Ensure you have the correct access key, deployment id, "\
                  f"and proxy service id as found in your Sermos Cloud console."
            raise ValueError(msg)
        data = proxy.get('data', {})
        conn_settings = data.get('connectionSettings', {})

        self.proxy_hostname = conn_settings['hostname']['value']
        self.proxy_port = conn_settings['nodeport']['value']

    def server(self, local_host: str, local_port: int, remote_host: str,
               remote_port: int, max_connection: int, tunnel_payload: dict):
        """ Establish our local server (this is what a local tool such as
            redis-cli would connect to, for example).
        """
        logger.info(f"[+] Local Server Starting {local_host}:{local_port} ...")
        local_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        local_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
                                       1)
        local_server_socket.bind((local_host, local_port))
        local_server_socket.listen(max_connection)
        logger.info(f"[+] Local Server Started {local_host}:{local_port} "
                    f"[{local_server_socket.fileno()}] ...")

        client_socket = None
        while True:
            try:
                # Look for new connections to our local server. These will
                # be things like a redis-cli command pointed to this local
                # proxy server.
                logger.info("[.] Waiting for local connections ...")

                client_socket, client_address = local_server_socket.accept()
                logger.info(f"[+] Detect connection from "
                            f"{client_address[0]}:{client_address[1]} "
                            f"{[client_socket.fileno()]}")

                try:
                    # Create a tunnel between the remote proxy server and
                    # the new local client socket. The remote proxy server
                    # will already be tunneling data to the desired remote
                    # service (e.g. cloud deployment of Redis) if the
                    # handshake above passed successfully.
                    slpc = SermosLocalProxyClient(
                        remote_host=remote_host,
                        remote_port=remote_port,
                        tunnel_payload=tunnel_payload)
                    slpc.connect()
                    slpc.start(client_socket)

                except (TunnelError, ProxyError) as e:
                    logger.error(e)
                    self._close_conn(client_socket)

                except Exception as e:
                    logger.error("[x] Tunnel exception ...")
                    try:
                        self._close_conn(client_socket)
                    except Exception as e:
                        logger.error(f"[x] Failed to close client socket: {e}")
                    break

            except KeyboardInterrupt:
                logger.info(
                    "[.] Manually closing local server. Cleaning up ...")
                if client_socket is not None:
                    self._close_conn(client_socket)
                break

            except Exception as e:
                logger.error(f"[x] Unknown Exception: {e}")
                break

        logger.info("[-] Releasing resources...")
        try:
            self._close_conn(remote_server_socket)
        except Exception as e:
            logger.error(f"[x] Unable to close remote proxy socket: {e}")
        try:
            self._close_conn(local_server_socket)
        except Exception as e:
            logger.error(f"[x] Unable to close local server socket: {e}")
        logger.info("[*] Server shuted down!")

    def connect(self, auto_select: bool = False):
        """ Establish proxy connection. This will communicate with Sermos Cloud
            to retrieve credentials that your Proxy Service will validate.

            auto_select: If true, no user prompts provided and we'll choose
                the first service and first port available.
        """
        logger.debug(f"Requesting connection details from {self.service_url}")
        self._get_service_info()
        self._get_proxy_info()
        self._get_jwt()
        self._determine_service_port(auto_select=auto_select)

        if self.debug:
            self.proxy_hostname = '127.0.0.1'
            self.proxy_port = 49152

        logger.info(
            f"\n    Local: {self.local_host}:{self.local_port}"
            f"\n    Proxy: {self.proxy_hostname}:{self.proxy_port}"
            f"\n    Dest:  {self.k8s_service_id}:{self.k8s_service_port}")

        # At this point, we have all of the credentials required to ask the
        # remote proxy (deployed in a Sermos Cloud deployment) to establish
        # a connection.
        tunnel_payload = {
            'jwt': self.proxy_token,
            'target_host': self.k8s_service_id,
            'target_port': self.k8s_service_port
        }

        self.server(self.local_host, self.local_port, self.proxy_hostname,
                    self.proxy_port, self.max_connection, tunnel_payload)
