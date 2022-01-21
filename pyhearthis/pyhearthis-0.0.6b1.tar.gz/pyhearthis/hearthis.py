from os import urandom
import aiohttp
import json
import re
from enum import Enum
from typing import List
from datetime import date, timedelta

from aiohttp.client_exceptions import InvalidURL
from .models import SingleArtist, SingleTrack, User, as_query_param, cast_dict, cast_list, LoggedinUser, Category, Playlist
from .hearthis_requests import AddToExistingPlaylistRequest, AddToNewPlaylistRequest, DeleteFromPlaylistRequest, FollowRequest, LoginRequest, LogoutRequest, FeedRequest, CredentialsRequest, PagedRequest, AddPlaylistRequest, PlaylistsRequest, DeletePlaylistRequest, SearchRequest, ArtistTracksRequest


class FeedType(Enum):
    UNDEFINED = 1
    POPULAR = 2
    NEW = 3


class SearchType(Enum):
    TRACKS = 1
    USER = 2,
    PLAYLISTS = 3


class ArtistTracklistType(Enum):
    LIKES = 1
    PLAYLISTS = 2,
    TRACKS = 3


class RequestError(Exception):
    pass


class DeletePlaylistError(Exception):
    pass


class HearThis:
    api_endpoint = "https://api-v2.hearthis.at/"

    @staticmethod
    def _replace_key(dictionary: dict, old_key: str, new_key: str) -> None:
        if old_key not in dictionary:
            return

        data = dictionary[old_key]
        dictionary.pop(old_key, None)
        dictionary[new_key] = data

    @staticmethod
    def _feed_type_as_string(type: FeedType) -> str:
        if type is FeedType.NEW:
            return "new"
        if type is FeedType.POPULAR:
            return "popular"

        return ""

    @staticmethod
    def _tracklist_type_as_string(type: ArtistTracklistType) -> str:
        if type is ArtistTracklistType.TRACKS:
            return "tracks"
        if type is ArtistTracklistType.LIKES:
            return "likes"
        if type is ArtistTracklistType.PLAYLISTS:
            return "playlists"

        return ""

    @staticmethod
    def _search_type_as_string(type: SearchType) -> str:
        if type is SearchType.TRACKS:
            return "tracks"
        if type is SearchType.USER:
            return "user"
        if type is SearchType.PLAYLISTS:
            return "playlists"

        return ""

    async def _get_as_bytes(self, url):
        try:
            async with self._client_session.get(url) as response:
                if response.status == 200:
                    return await response.read()
                return None
        except InvalidURL:
            return None

    async def _get_as_json(self, route, request=None):
        query = f"{HearThis.api_endpoint}{route}"

        if request is not None:
            param = as_query_param(request)
            query = query + f"?{param}"

        async with self._client_session.get(query) as response:
            json_data = await response.json()

            if json_data is None:
                return dict()

            if 'success' in json_data:
                if json_data['success'] is False:
                    return dict()
            
            if isinstance(json_data, list):
                return list(filter(lambda itm: not isinstance(itm, bool), json_data))
            
            return json_data

    async def _get_as_text(self, route, request=None, with_endpoint: bool = True):
        endpoint = HearThis.api_endpoint if with_endpoint else ""
        query = f"{endpoint}{route}"

        if request is not None:
            param = as_query_param(request)
            query = query + f"?{param}"

        async with self._client_session.get(query) as response:
            if response.status != 200:
                return ""

            return await response.text()

    async def _post_json(self, route, request, expected_status_code: int = 201):
        url = f"{HearThis.api_endpoint}{route}"
        data = json.dumps(cast_dict(request._asdict()))

        async with self._client_session.post(url, json=data) as response:
            if response.status != expected_status_code:
                raise RequestError()

            if response.content_type == "text/html":
                return await response.text()

            return await response.json()

    async def _post_as_form_data(self, route, request, expected_status_code: int = 201, force_json: bool = False):
        url = f"{HearThis.api_endpoint}{route}"
        payload = cast_dict(request._asdict(), True)

        async with self._client_session.post(url, data=payload) as response:
            if response.status != expected_status_code:
                raise RequestError()

            if response.content_type == "text/html" and not force_json:
                return await response.text()

            return await response.json()

    @staticmethod
    def _json_to_track(json_dict: dict) -> SingleTrack:
        user_dict = json_dict.pop("user")
        return SingleTrack(**json_dict, user=User(**user_dict))

    @staticmethod
    def _json_to_playlist(json_dict: dict) -> Playlist:
        user_dict = json_dict.pop("user")
        return Playlist(**json_dict, user=User(**user_dict))

    def __init__(self, client_session: aiohttp.ClientSession) -> None:
        self._client_session = client_session

    async def login(self, email: str, password: str) -> LoggedinUser:
        json_data = await self._get_as_json("login", LoginRequest(email, password))
        HearThis._replace_key(json_data, "720p_url", "p_url")
        return LoggedinUser(**cast_dict(json_data))

    async def logout(self, user: LoggedinUser) -> bool:
        request = LogoutRequest(user.key, user.secret)

        param = as_query_param(request)
        query = f"{HearThis.api_endpoint}logout?{param}"
        async with self._client_session.get(query) as response:
            status = await response.status
            return status == 200

    async def get_categories(self) -> List[Category]:
        json_data = await self._get_as_json("categories/")
        return list(map(lambda data: Category(**data), json_data))

    async def get_waveform_data(self, track: SingleTrack) -> str:
        return await self._get_as_text(track.waveform_data, with_endpoint=False)

    async def get_feeds(self, user: LoggedinUser, category: str = "", feed_type=FeedType.UNDEFINED, duration: timedelta = None, page: int = 1, count: int = 5, feed_start: date = None, feed_end: date = None) -> List[SingleTrack]:
        assert count <= 20, 'maximum allowed pagecount is 20'

        start = None if feed_start is None else feed_start.strftime("%Y-%m-%d")
        end = None if feed_end is None else feed_end.strftime("%Y-%m-%d")

        duration_in_minutes = None if duration is None else round(duration.total_seconds() / 60)
        request = FeedRequest(user.key, user.secret, duration_in_minutes, HearThis._feed_type_as_string(feed_type), category, start, end, page, count)

        json_data = await self._get_as_json("feed/", request)
        return list(map(HearThis._json_to_track, cast_list(json_data)))

    async def get_category_tracks(self, user: LoggedinUser, category: Category, page: int = 1, count: int = 5) -> List[SingleTrack]:
        assert count <= 20, 'maximum allowed pagecount is 20'

        route = f"categories/{category.id}"
        json_data = await self._get_as_json(route, PagedRequest(user.key, user.secret, page, count))
        return list(map(HearThis._json_to_track, cast_list(json_data)))

    async def get_artist_tracks(self, user: LoggedinUser, user_permalink: str, track_type: ArtistTracklistType = ArtistTracklistType.TRACKS, page: int = 1, count: int = 5) -> List[SingleTrack]:
        assert count <= 20, 'maximum allowed pagecount is 20'

        route = f"{user_permalink}/"
        json_data = await self._get_as_json(route, ArtistTracksRequest(user.key, user.secret, HearThis._tracklist_type_as_string(track_type), page, count))
        return list(map(HearThis._json_to_track, cast_list(json_data)))

    async def get_playlists(self, user: LoggedinUser, page: int = 1, count: int = 5) -> List[Playlist]:
        assert count <= 20, 'maximum allowed pagecount is 20'

        route = f"{user.permalink}"
        json_data = await self._get_as_json(route, PlaylistsRequest(user.key, user.secret, page, count))
        return list(map(HearThis._json_to_playlist, cast_list(json_data)))

    async def create_playlist(self, user: LoggedinUser, playlist_name: str, private_set: bool = True) -> None:
        route = "set_ajax_add.php"
        privat = 1 if private_set else 0
        await self._post_as_form_data(route, AddPlaylistRequest(user.key, user.secret, playlist_name, privat=privat), 200)

    async def add_track_to_playlist(self, user: LoggedinUser, track: SingleTrack, playlist: Playlist) -> Playlist:
        route = "set_ajax_add.php"
        json_str = await self._post_as_form_data(route, AddToExistingPlaylistRequest(user.key, user.secret, track.id, playlist.id), 200)
        obj = json.loads(json_str)
        return Playlist(**cast_dict(obj))

    async def add_track_to_new_playlist(self, user: LoggedinUser, track: SingleTrack, playlist_name: str):
        route = "set_ajax_add.php"
        json_str = await self._post_as_form_data(route, AddToNewPlaylistRequest(user.key, user.secret, track.id, playlist_name), 200)
        obj = json.loads(json_str)
        return Playlist(**cast_dict(obj))

    async def get_playlist_tracks(self, user: LoggedinUser, playlist: Playlist) -> List[SingleTrack]:
        route = f"set/{playlist.permalink}/"
        json_data = await self._get_as_text(route, CredentialsRequest(user.key, user.secret), 200)
        if json_data == '':
            return []

        return list(map(HearThis._json_to_track, cast_list(json.loads(json_data))))

    async def delete_track_from_playlist(self, user: LoggedinUser, track: SingleTrack, playlist: Playlist) -> Playlist:
        route = "set_ajax_add.php"
        json_str = await self._post_as_form_data(route, DeleteFromPlaylistRequest(user.key, user.secret, track.id, playlist.id), 200)
        obj = json.loads(json_str)
        return Playlist(**cast_dict(obj))

    async def delete_playlist(self, user: LoggedinUser, playlist: Playlist) -> None:
        route = "set_ajax_edit.php"
        response = await self._post_as_form_data(route, DeletePlaylistRequest(user.key, user.secret, playlist.id), 200)
        if response != 'DELETED':
            raise DeletePlaylistError()

    async def search(self, user: LoggedinUser, query: str, search_type: SearchType = None, duration: timedelta = None, page: int = 1, count: int = 5) -> List[SingleTrack]:
        assert count <= 20, 'maximum allowed pagecount is 20'

        route = "search/"
        duration_in_minutes = None if duration is None else round(duration.total_seconds() / 60)
        type = None if search_type is None else self._search_type_as_string(search_type)

        request = SearchRequest(user.key, user.secret, query, type, duration_in_minutes, page, count)
        json_data = await self._get_as_json(route, request)

        return list(map(HearThis._json_to_track, cast_list(json_data)))

    async def reload_single_track(self, user: LoggedinUser, track: SingleTrack) -> SingleTrack:
        route = f"{track.user.permalink}/{track.permalink}"
        data = await self._get_as_json(route)
        return HearThis._json_to_track(data)

    async def get_single_artist(self, user: LoggedinUser, permalink: str) -> SingleArtist:
        route = f"{permalink}"
        json_data = await self._get_as_json(route)
        self._replace_key(json_data, "720p_url", "p_url")
        return SingleArtist(**cast_dict(json_data))

    async def download_track(self, user: LoggedinUser, track: SingleTrack) -> bytes:
        return await self._get_as_bytes(track.download_url)

    async def toggle_follow_user_from_track(self, user: LoggedinUser, track: SingleTrack) -> bool:
        
        artist = await self.get_single_artist(user, track.user.permalink)
        if not artist.following:
            route = "user_ajax_function.php"
            response = await self._post_as_form_data(route, FollowRequest(user.key, user.secret, track.user.id), 200)
            data = json.loads(response)
            return data["follow"]
