# Copyright 2022 XXIV
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import http.client as client
from types import SimpleNamespace
import json
from urllib.parse import quote_plus


def http(endpoint):
    try:
        conn = client.HTTPSConnection('www.theaudiodb.com')
        conn.request('GET', f'/api/v1/json/2/{endpoint}')
        data = conn.getresponse().read().decode('UTF-8')
        conn.close()
        return data
    except:
        return None


def search_artist(s: str):
    """
    :param s:
    :return: Artist details from artist name
    """
    try:
        response = http(f"search.php?s={quote_plus(s)}")
        if response is not None and len(response) != 0:
            data = json.loads(response, object_hook=lambda d: SimpleNamespace(**d))
            if data.artists is not None:
                return data.artists[0]
            else:
                return None
        else:
            return None
    except:
        return None


def discography(s: str):
    """
    :param s:
    :return: Discography for an Artist with Album names and year only
    """
    try:
        response = http(f"discography.php?s={quote_plus(s)}")
        if response is not None and len(response) != 0:
            data = json.loads(response, object_hook=lambda d: SimpleNamespace(**d))
            if data.album is not None:
                return data.album
            else:
                return None
        else:
            return None
    except:
        return None


def search_artist_by_id(i: int):
    """
    :param i:
    :return: individual Artist details using known Artist ID
    """
    try:
        response = http(f"artist.php?i={i}")
        if response is not None and len(response) != 0:
            data = json.loads(response, object_hook=lambda d: SimpleNamespace(**d))
            if data.artists is not None:
                return data.artists[0]
            else:
                return None
        else:
            return None
    except:
        return None


def search_album_by_id(i: int):
    """
    :param i:
    :return: individual Album info using known Album ID
    """
    try:
        response = http(f"album.php?m={i}")
        if response is not None and len(response) != 0:
            data = json.loads(response, object_hook=lambda d: SimpleNamespace(**d))
            if data.album is not None:
                return data.album[0]
            else:
                return None
        else:
            return None
    except:
        return None


def search_albums_by_artist_id(i: int):
    """
    :param i:
    :return: All Albums for an Artist using known Artist ID
    """
    try:
        response = http(f"album.php?i={i}")
        if response is not None and len(response) != 0:
            data = json.loads(response, object_hook=lambda d: SimpleNamespace(**d))
            if data.album is not None:
                return data.album
            else:
                return None
        else:
            return None
    except:
        return None


def search_tracks_by_album_id(i: int):
    """
    :param i:
    :return: All Tracks for Album from known Album ID
    """
    try:
        response = http(f"track.php?m={i}")
        if response is not None and len(response) != 0:
            data = json.loads(response, object_hook=lambda d: SimpleNamespace(**d))
            if data.track is not None:
                return data.track
            else:
                return None
        else:
            return None
    except:
        return None


def search_track_by_id(i: int):
    """
    :param i:
    :return: individual track info using a known Track ID
    """
    try:
        response = http(f"track.php?h={i}")
        if response is not None and len(response) != 0:
            data = json.loads(response, object_hook=lambda d: SimpleNamespace(**d))
            if data.track is not None:
                return data.track[0]
            else:
                return None
        else:
            return None
    except:
        return None


def search_music_videos_by_artist_id(i: int):
    """
    :param i:
    :return: Return all the Music videos for a known Artist ID
    """
    try:
        response = http(f"mvid.php?i={i}")
        if response is not None and len(response) != 0:
            data = json.loads(response, object_hook=lambda d: SimpleNamespace(**d))
            if data.mvids is not None:
                return data.mvids
            else:
                return None
        else:
            return None
    except:
        return None