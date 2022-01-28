from kabaret import flow

from libreflow import baseflow
from .departments import PlayLastBlastAction


class Bookmark(baseflow.users.Bookmark):

    play_last_playblast = flow.Child(PlayLastBlastAction)
