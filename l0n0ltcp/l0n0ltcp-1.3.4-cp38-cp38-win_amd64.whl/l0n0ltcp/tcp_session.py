import asyncio
from l0n0ltcp.runner import is_process_closed
import logging
from l0n0ltcp.tcp_proto_base import TcpProtoBase
from l0n0ltcp.tcp_callback_base import TcpCallbackBase


class TcpSession:
    def __init__(self,
                 owner,
                 id: int,
                 r: asyncio.StreamReader,
                 w: asyncio.StreamWriter,
                 heart_interval: float,
                 max_no_msg_count: int,
                 proto: TcpProtoBase,
                 cb: TcpCallbackBase) -> None:
        self.owner = owner
        self.id = id
        self.reader = r
        self.writer = w
        self.proto = proto
        self.cb = cb
        self.heart_interval = heart_interval
        self.max_no_msg_count = max_no_msg_count
        self.no_msg_count = 0
        self.extra_info = None
        self.send_buffer = []

    def avalible(self):
        return self.reader is not None \
            and self.writer is not None \
            and not self.writer.is_closing() \
            and not self.reader.at_eof() \
            and not is_process_closed()

    def _heart(self):
        try:
            if not self.avalible() or self.heart_interval <= 0:
                return

            if self.max_no_msg_count > 0:
                self.no_msg_count += 1
                if self.no_msg_count >= self.max_no_msg_count:
                    self.writer.close()

            heart_msg = self.proto.make_heart_msg()
            if heart_msg:
                self.writer.write(heart_msg)

            asyncio.get_running_loop().call_later(self.heart_interval, self._heart)
        except:
            pass

    def start_heart(self):
        if not self.reader or not self.writer or self.writer.is_closing() or self.heart_interval <= 0:
            return
        asyncio.get_running_loop().call_later(self.heart_interval, self._heart)

    async def run(self):
        try:
            await self.cb.on_connect(self)

            if self.avalible():
                for msg in self.send_buffer:
                    self.send_msg(msg)
            self.send_buffer.clear()

            while self.avalible():
                msg_data = await self.proto.read_msg(self)
                self.no_msg_count = 0
                if msg_data is None:
                    continue
                try:
                    ret = await self.cb.on_msg(self, msg_data)
                    if ret is None:
                        continue
                    self.send_msg(ret)
                except Exception as e:
                    logging.error(
                        f"On msg {msg_data} error! exception = " +
                        str(e.with_traceback(None)),
                        stack_info=True)
        except Exception as e:
            pass

        if self.writer:
            self.writer.close()
        self.reader = None
        self.writer = None

        try:
            await self.cb.on_close(self)
        except Exception as e:
            logging.error(e.with_traceback(None))

        try:
            await self.owner.on_session_close(self.id)
        except Exception as e:
            logging.error(e.with_traceback(None))

    def send_msg(self, data: bytes):
        try:
            if not self.writer or self.writer.is_closing():
                return False
            data = self.proto.build_msg(data)
            self.writer.write(data)
        except Exception as e:
            logging.error(f"send msg error: {e.with_traceback(None)}")
            return False
        return True

    def close(self):
        try:
            if not self.writer or self.writer.is_closing():
                return
            self.writer.close()
            self.reader = None
            self.writer = None
        except:
            pass

    async def drain(self):
        try:
            await self.writer.drain()
        except Exception as e:
            logging.error(f"drain error: {e.with_traceback(None)}")
            return False
        return True