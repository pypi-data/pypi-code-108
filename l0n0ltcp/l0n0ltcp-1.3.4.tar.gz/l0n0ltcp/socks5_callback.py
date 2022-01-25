from l0n0ltcp.tcp_proto_base import TcpProtoBase
from l0n0ltcp.tcp_callback_base import TcpCallbackBase
from l0n0ltcp.socks5_enums import Socks5ServerState
from l0n0ltcp.tcp_client import TcpClient
from struct import pack, unpack
import socket


class Socks5RemoteClientCallback(TcpCallbackBase):
    def __init__(self, session) -> None:
        self.session = session

    async def on_connect(self, session):
        s = session.writer.get_extra_info('socket')
        bind_addr = s.getsockname()
        addr = unpack("!I", socket.inet_aton(bind_addr[0]))[0]
        port = bind_addr[1]
        if s.family == socket.AddressFamily.AF_INET:
            address_type = 1
        elif s.family == socket.AddressFamily.AF_INET6:
            address_type = 4
        self.session.send_msg(
            pack("!BBBBIH", 5, 0, 0, address_type, addr, port))
        self.session.extra_info['state'] = Socks5ServerState.TransData

    async def on_close(self, session):
        self.session.close()

    async def on_msg(self, session, data):
        self.session.send_msg(data)


class Socks5ServerCallback(TcpCallbackBase):
    async def on_connect(self, session):
        session.extra_info = {
            "state": Socks5ServerState.ReadMethods
        }

    async def on_close(self, session):
        if session.extra_info:
            client = session.extra_info.get('client')
            if client:
                client.close()

    async def on_msg(self, session, data):
        state = session.extra_info['state']
        if state == Socks5ServerState.ReadMethods:
            session.send_msg(b'\x05\x00')
            session.extra_info['state'] = Socks5ServerState.ReadCmd
        elif state == Socks5ServerState.ReadCmd:
            cmd = data[0]
            address = data[1]
            port = data[2]
            if cmd == 1:  # CONNECT
                client = TcpClient(
                    address, port, 
                    Socks5RemoteClientCallback(session), 
                    TcpProtoBase())
                client.start()
                session.extra_info['client'] = client
                session.extra_info['state'] = Socks5ServerState.WaitConnect
                session.extra_info['data_cache'] = []
            elif cmd == 2:  # BIND
                pass
            elif cmd == 3:  # UDP ASSOCIATE
                pass
        elif state == Socks5ServerState.WaitConnect:
            session.extra_info['data_cache'].append(data)
        elif state == Socks5ServerState.TransData:
            client = session.extra_info.get("client")
            data_cache = session.extra_info.get("data_cache")
            if data_cache and len(data_cache) > 0:
                for msg in data_cache:
                    client.send_msg(msg)
                del session.extra_info['data_cache']
            client.send_msg(data)
