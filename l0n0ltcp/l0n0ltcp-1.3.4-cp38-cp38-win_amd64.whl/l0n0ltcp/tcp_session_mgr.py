import asyncio
from l0n0ltcp.tcp_session import TcpSession
from l0n0ltcp.tcp_proto_base import TcpProtoBase
from l0n0ltcp.tcp_callback_base import TcpCallbackBase


class TcpSessionMgr:
    def __init__(self,
                 cb: TcpCallbackBase,
                 proto: TcpProtoBase,
                 heartbeat_interval: float = 0,
                 max_no_msg_count: int = 0) -> None:
        self.sessions = {}
        self.max_session_id = 0
        self.handlers = {}
        self.cb = cb
        self.proto = proto
        self.heartbeat_interval = heartbeat_interval
        self.max_no_msg_count = max_no_msg_count

    async def on_new_session(self, r: asyncio.StreamReader, w: asyncio.StreamWriter, msgs_after_connect: list = []):
        self.max_session_id += 1
        session = TcpSession(self,
                             self.max_session_id,
                             r, w,
                             self.heartbeat_interval,
                             self.max_no_msg_count,
                             self.proto,
                             self.cb)
        self.sessions[self.max_session_id] = session
        session.start_heart()
        session.send_buffer += msgs_after_connect
        await session.run()

    async def on_session_close(self, id: int):
        del self.sessions[id]

    def close(self, session_id=None):
        if session_id is None:
            for session in self.sessions.values():
                session.close()
        else:
            session = self.sessions.get(session_id)
            if session is None:
                return
            session.close()
