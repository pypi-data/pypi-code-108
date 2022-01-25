import json
import logging
from collections import UserDict
from pathlib import Path
from uuid import uuid4

import ffmpeg
import filetype
import pendulum

log = logging.getLogger(__name__)


class Datum(UserDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uuid = self["uuid"] = str(uuid4())
        self.load_dt = pendulum.now()
        self["load_dt"] = self.load_dt.to_iso8601_string()
        # special case: files haves paths. we have lots of files.
        if "path" in self:
            self.path = Path(self.pop("path"))
            self["path"] = str(self.path)
            self["filename"] = self.path.name
            self["uri"] = self.path.absolute().as_uri()
            self["filetype"] = self._guess_filetype()
            self["stat"] = self._stat()
            # TODO EAFP instead of LBYL
            if self._is_video():
                self["ffprobe"] = self._ffprobe()

    # ignore when None is passed as value
    def update(self, *args, **kwargs):
        if len(args) == 1 and args[0] is None:
            return
        else:
            super().update(*args)
        super().update(**kwargs)

    def __setitem__(self, key, value):
        if value is None:
            log.debug(f"{key} is None")
            return
        super().__setitem__(key, value)

    # -----------------------------------

    # file handling (maybe refac this)
    def _guess_filetype(self):
        x = filetype.guess(str(self.path))
        if x is not None:
            return {"extension": x.extension, "mime": x.mime}

    def _stat(self):
        s = self.path.stat()
        attrs = [a for a in dir(s) if a.startswith("st_")]
        return {a: getattr(s, a) for a in attrs}

    def _ffprobe(self):
        return ffmpeg.probe(self.path)

    def _is_video(self):
        try:
            return self["filetype"]["mime"].startswith("video/")
        except KeyError:
            return False

    # -------------

    def to_json(self):
        return json.dumps(self.data, sort_keys=True, indent=2)
