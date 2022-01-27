import lzma
import struct
from .binary import Binary
from .models import ReplayEvent
from .mod import Mod
from datetime import datetime, timedelta

class Replay(Binary):

    def __init__(self, replay_data, pure_lzma=False):
        super().__init__(replay_data)
        if pure_lzma:
            self.replay_data = self._parse_replay_data(pure_lzma)
        else:
            self._parse()

    def _parse(self):
        self.game_mode = self.readByte()
        self.game_version = self.readInt()
        self.beatmap_hash = self.readString()
        self.player_name = self.readString()
        self.replay_hash = self.readString()
        self.count_300 = self.readShort()
        self.count_100 = self.readShort()
        self.count_50 = self.readShort()
        self.count_geki = self.readShort()
        self.count_katu = self.readShort()
        self.count_miss = self.readShort()
        self.score = self.readInt()
        self.max_combo = self.readShort()
        self.perfect = self.readBool()
        self.mods = Mod(self.readInt())
        self.hp_graph = self.readString()
        self.timestamp = datetime.min + timedelta(microseconds=self.readLong()/10)
        self.replay_size = self.readInt()
        self.replay_data = self._parse_replay_data()
        self.score_id = self.readLong()

    def _parse_replay_data(self, pure_lzma=False):
        if pure_lzma:
            data = lzma.decompress(self.data,
                format=lzma.FORMAT_AUTO).decode("ascii")[:-1]
        else:
            start = self.offset
            self.offset += self.replay_size
            data = lzma.decompress(self.data[start:self.offset],
                format=lzma.FORMAT_AUTO).decode("ascii")[:-1]
        events = [eventstring.split("|") for eventstring in data.split(",")]

        replay_data = []
        t = 0

        for event in events:
            t += int(event[0])
            replay_data.append(ReplayEvent(t, int(event[0]),
                float(event[1]), float(event[2]), int(event[3])))

        if len(replay_data) > 0 and replay_data[-1].frametime == -12345:
            del replay_data[-1]

        return replay_data

class ReplayPath(Replay):
    def __init__(self, replay_path):
        with open(replay_path, "rb") as f:
            replay_data = f.read()
        super().__init__(replay_data)
