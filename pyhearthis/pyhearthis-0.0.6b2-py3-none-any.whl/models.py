from datetime import datetime
from typing import NamedTuple, Any
from urllib.parse import urlencode

def is_not_empty(item) -> bool:
    if item is None:
        return ""

    if isinstance(item, str):
        return len(item.strip()) > 0
    
    return True

def as_query_param(item: NamedTuple) -> str:
    dictionary = {k:v for (k,v) in item._asdict().items() if is_not_empty(v)}
    return urlencode(dictionary)

def get_value(key, value):
    
    if key == "downloadable":
        return True if (value == 1) or value == '1' else False

    if key == "bpm":
        return float(value)
    
    if key == "id" or key == "user_id" or key == "duration" or key == "release_timestamp" or key=="track_id" or key=="set" or key=="set_id" or "count" in key:
        if value is None:
            return int(0)
        
        return int(value)

    return value

def cast_dict(items: dict, omit_empty: bool=False) -> dict:
    if omit_empty:
        return {k:get_value(k, v) for (k,v) in items.items() if is_not_empty(v) }

    return {k:get_value(k, v) for (k,v) in items.items() }

def cast_list(items: dict) -> list:
    return list(map(cast_dict, items))

class LoggedinUser(NamedTuple):

    id: int
    permalink: str
    username: str
    caption: str
    uri: str
    permalink_url: str
    thumb_url: str
    avatar_url: str
    p_url: str
    background_url: str
    description: str
    geo: str
    track_count: int
    playlist_count: int
    likes_count: int
    followers_count: int
    following_count: int
    following: int
    premium: int
    allow_push: int
    email: str
    locale: str
    secret: str
    key: str

class User(NamedTuple):
    id: int
    permalink: str
    username: str
    uri: str
    permalink_url: str
    avatar_url: str
    caption: str = ''

class Category(NamedTuple):
    id: str
    name: str
    url: str
    api_url: str

class SingleTrack(NamedTuple):
    id: int
    created_at: datetime
    private: int
    release_date: datetime
    release_timestamp: int
    geo: str
    user_id: int
    duration: int
    permalink: str
    description: str
    downloadable: bool
    genre: str
    genre_slush: str
    title: str
    uri: str
    permalink_url: str
    thumb: str
    artwork_url: str
    background_url: str
    waveform_data: str
    waveform_url: str
    user: User
    stream_url: str
    download_url: str
    playback_count: int
    download_count: int
    favoritings_count: int
    favorited: bool
    comment_count: int
    tags: str
    taged_artists: str
    bpm: float
    key: str
    type: str
    license: str
    version: str
    artwork_url_retina: str
    preview_url: str
    download_filename: str
    reshares_count: int
    reshared: bool
    played: bool
    liked: bool
    fan_exclusive_play: int = 0
    fan_exclusive_download: int = 0

class Playlist(NamedTuple):
    id: int
    user_id: int
    permalink: str
    title: str
    description: str
    privat: bool
    uri: str
    permalink_url: str
    thumb: str
    artwork_url: str
    track_count: int
    user: User

class SingleArtist(NamedTuple):
    id: int
    permalink: str
    username: str
    uri: str
    permalink: str
    permalink_url: str
    avatar_url: str
    background_url: str
    description: str
    track_count: int
    playlist_count: int
    likes_count: int
    followers_count: int
    following: bool
    following_count: int
    premium: bool
    allow_push: int
    geo: str
    p_url: str
    avatar_url: str
    thumb_url: str
    caption: str




