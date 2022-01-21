from typing import NamedTuple
from datetime import datetime


class LoginRequest(NamedTuple):
    email: str
    password: str


class LogoutRequest(NamedTuple):
    key: str
    secret: str


class CredentialsRequest(NamedTuple):
    key: str
    secret: str


class PagedRequest(NamedTuple):
    key: str
    secret: str
    page: int = 1
    count: int = 5


class PlaylistsRequest(NamedTuple):
    key: str
    secret: str
    page: int = 1
    count: int = 5
    type: str = 'playlists'


class FeedRequest(NamedTuple):
    key: str
    secret: str
    duration: int
    type: str
    category: str
    show_feed_start: datetime
    show_feed_end: datetime
    page: int = 1
    count: int = 5


class AddPlaylistRequest(NamedTuple):
    key: str
    secret: str
    new_set: str
    category: str = ''
    source: str = ''
    privat: int = 1
    sort_config: int = 1
    action: str = "createnew"


class AddToExistingPlaylistRequest(NamedTuple):
    key: str
    secret: str
    track_id: int
    set: int
    action: str = 'add'


class AddToNewPlaylistRequest(NamedTuple):
    key: str
    secret: str
    track_id: int
    new_set: str
    action: str = 'add'


class DeleteFromPlaylistRequest(NamedTuple):
    key: str
    secret: str
    id: int
    set_id: int
    action: str = 'deleteentry'


class GetPlaylistItemsRequest(NamedTuple):
    key: str
    secret: str
    setid: int


class DeletePlaylistRequest(NamedTuple):
    key: str
    secret: str
    set: int
    action: str = 'delete'


class SearchRequest(NamedTuple):
    key: str
    secret: str
    t: str
    type: str = None
    duration: int = None
    page: int = 1
    count: int = 5


class ArtistTracksRequest(NamedTuple):
    key: str
    secret: str
    type: str
    page: int = 1
    count: int = 5

class FollowRequest(NamedTuple):
    key: str
    secret: str
    userid: str
    action: str = 'follow'
