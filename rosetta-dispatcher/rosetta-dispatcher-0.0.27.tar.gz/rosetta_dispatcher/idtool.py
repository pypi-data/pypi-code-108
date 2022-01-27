import os
import uuid


class IdTool(object):
    def __init__(self):
        self.uuid_node = os.getpid() ^ uuid.getnode()
        self.clock_seq = 0

    @classmethod
    def get_timestamp(cls, struuid: str):
        return (uuid.UUID(struuid).time - 0x01b21dd213814000) / 1e7

    def gen_uuid(self):
        self.clock_seq += 1
        return str(uuid.uuid1(self.uuid_node, self.clock_seq))


idtool = IdTool()
