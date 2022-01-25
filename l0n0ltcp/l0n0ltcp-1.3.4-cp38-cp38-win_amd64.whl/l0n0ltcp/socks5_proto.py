from l0n0ltcp.socks5_enums import Socks5ServerState
from l0n0ltcp.tcp_proto_base import TcpProtoBase
import struct
import socket

class Socks5ServerProto(TcpProtoBase):
    def build_msg(self, data: bytes) -> bytes:
        return data

    async def read_msg(self, session):
        state = session.extra_info['state']
        if state == Socks5ServerState.ReadMethods:
            # 交换验证方法
            data = await session.reader.readexactly(2)
            version, nmethods = struct.unpack("!BB", data)
            if version != 5:
                session.close()
                return
            methods = await session.reader.readexactly(nmethods)
            return (version, methods)
        elif state == Socks5ServerState.ReadCmd:
            # 获取指令
            version, cmd, _, address_type = struct.unpack("!BBBB", await session.reader.readexactly(4))
            if address_type == 1:  # IPv4 
                host = socket.inet_ntoa(await session.reader.readexactly(4)) 
            elif address_type == 3:  # Domain name 
                domain_length = ord(await session.reader.readexactly(1)) 
                host = await session.reader.readexactly(domain_length)
            elif address_type == 4:  # Domain name 
                host = await session.reader.readexactly(16)
            port = struct.unpack("!H", await session.reader.readexactly(2))[0]
            return (cmd, host, port)
        elif state == Socks5ServerState.WaitConnect \
        or state == Socks5ServerState.TransData:
            data = await session.reader.read(4096)
            if len(data) <= 0:
                session.close()
                return
            return data