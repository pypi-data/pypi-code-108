from typing import Optional

from .internal import config_getter, config_spawn


class Client:
    def __init__(self, proxy: Optional[int] = None):
        self.cfg = config_getter.read_cfg()
        self.yt_dl = config_spawn.spawn_usable_config(proxy=proxy)
        self.load_all_config()

    def load_all_config(self):
        youtube_only: str = self.cfg.get("youtube_only")
        if youtube_only == "True":
            self.yt_only = True
        else:
            self.yt_only = False
