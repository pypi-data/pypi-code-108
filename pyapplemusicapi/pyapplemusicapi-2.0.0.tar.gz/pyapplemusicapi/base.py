# -*- coding: utf-8 -*-
"""This module contains base data models for the rest of the iTunes Store API
"""

import requests
import sys
from cachecontrol import CacheControl
from datetime import datetime
from pyapplemusicapi import API_HOST_NAME
from .exceptions import *

__all__ = ['TS_FORMAT', 'SESSION', 'BaseObject', 'Resource', 'Artist', 'Album', 'Track', 'Audiobook', 'Software', 'TVEpisode', 'lookup', 'lookup_upc', 'Lookup', 'LookupUPC']

#: iTunes API Timestamp format
TS_FORMAT = '%Y-%m-%dT%H:%M:%S'

#: Globally accessible cache-enabled requests session
SESSION = CacheControl(requests.session())



class BaseObject(object):
    """Base object for representing an iTunes request"""
    resource = None

    def __init__(self, **kwargs):
        self._search_terms = {k: v for (k, v) in list(kwargs.items())
                              if v is not None}
        self.json = None
        self.num_results = None

    @property
    def url(self):
        """The url pointing at the resource defined by the implementing object
        """
        return '{host}/{resource}'.format(host=API_HOST_NAME,
                                         resource=self.resource)

    def get(self):
        """Execute an HTTP GET against the iTunes API and construct an
        appropriate assortment of :class:`Resource`'s based on the response
        """
        response = SESSION.get(self.url, params=self._search_terms)
        try:
            self.json = response.json()
        except:
            raise NoResultsFoundException()

        if 'errorMessage' in self.json:
            raise ITunesException(self.json['errorMessage'])

        self.num_results = self.json['resultCount']
        l = []
        for json in self.json['results']:
            typ = None
            if 'wrapperType' in json:
                typ = json['wrapperType']
            elif 'kind' in json:
                typ = json['kind']

            if typ == 'artist':
                id_ = json['artistId']
                item = Artist(id_)
            elif typ == 'collection':
                id_ = json['collectionId']
                item = Album(id_)
            elif typ == 'track':
                id_ = json['trackId']

                if 'kind' in json:
                    kind = json['kind']
                    if kind == 'tv-episode':
                        item = TVEpisode(id_)
                    else:
                        item = Track(id_)
                else:
                    item = Track(id_)
            elif typ == 'audiobook':
                id_ = json['collectionId']
                item = Audiobook(id_)
            elif typ == 'software':
                id_ = json['trackId']
                item = Software(id_)
            else:
                if 'collectionId' in json:
                    id_ = json['collectionId']
                elif 'artistId' in json:
                    id_ = json['artistId']
                item = Resource(id_)
            item._set(json)
            l.append(item)
        return l


class Resource(object):
    """Base class for the various types of Resources returned by the iTunes
    Store API
    """

    def __init__(self, id):
        self.id = id
        self.name = None
        self.url = None
        self._release_date = None
        self.artwork = dict()

    def _set(self, json):
        """Construct this resource based on the provided JSON data"""
        self.json = json
        if 'kind' in json:
            self.type = json['kind']
        else:
            self.type = json['wrapperType']
        # Resource information
        self.genre = json.get('primaryGenreName', None)

        self.release_date_raw = json.get('releaseDate', '')
        self.country_store = json.get('country', None)
        self._set_artwork(json)
        self._set_url(json)

    @property
    def release_date(self):
        """Accessor for a :class:`datetime.datetime` representation of the
        release date for this :class:`Resource`
        """
        if not self.release_date_raw:
            return None

        if self._release_date is None:
            rd = self.release_date_raw.split('Z')[0]
            self._release_date = datetime.strptime(rd, TS_FORMAT)
        return self._release_date

    def _set_artwork(self, json):
        """Set the artwork urls from the json data"""
        if 'artworkUrl30' in json:
            self.artwork['30'] = json['artworkUrl30']
        if 'artworkUrl60' in json:
            self.artwork['60'] = json['artworkUrl60']
            self.artwork['600'] = self.artwork['60'].replace('60x60',
                                                             '600x600')
        if '' in json:
            self.artwork['100'] = json['artworkUrl100']
        if 'artworkUrl512' in json:
            self.artwork['512'] = json['artworkUrl512']

    def _set_url(self, json):
        self.url = None
        if 'trackViewUrl' in json:
            self.url = json['trackViewUrl']
        elif 'collectionViewUrl' in json:
            self.url = json['collectionViewUrl']
        elif 'artistViewUrl' in json:
            self.url = json['artistViewUrl']

    def __repr__(self):
        if not self.name:
            return '<{type}>: {id}'.format(type=self.type.title(), id=self.id)

        name = self.name
        if sys.version_info[0] == 2:
            name = self.name.encode('utf8')
        return '<{type}>: {name}'.format(type=self.type.title(), name=name)

    def __eq__(self, other):
        if not hasattr(other, 'id'): return False
        return self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_tracks(self, limit=500):
        """Returns the tracks associated with this :class:`Resource`"""
        if self.type == 'song':
            return self
        items = Lookup(id=self.id, entity='song', limit=limit).get()
        if not items:
            raise NoResultsFoundException()
        return items[1:]

    def get_albums(self, limit=200):
        """Returns the albums associated with this :class:`Resource`"""
        if self.type == 'collection':
            return self
        if self.type == 'song':
            return self.get_album()
        items = Lookup(id=self.id, entity='album', limit=limit).get()
        if not items:
            raise NoResultsFoundException()
        return items[1:]

    def get_album(self):
        """Returns the first album associated with this :class:`Resource`"""
        if self.type == 'collection':
            return self
        items = Lookup(id=self.id, entity='album', limit=1).get()
        if not items or len(items) == 1:
            raise NoResultsFoundException()
        return items[1]


class Artist(Resource):
    """The Artist :class:`Resource` represents an iTunes artist"""

    def _set(self, json):
        super(Artist, self)._set(json)
        self.name = json['artistName']
        self.amg_id = json.get('amgArtistId', None)
        self.url = json.get('artistViewUrl', json.get('artistLinkUrl', None))


class Album(Resource):
    """The Album :class:`Resource` represents an Album (or collection of single
    resources) of other resource types
    """

    def _set(self, json):
        super(Album, self)._set(json)
        self.name = json['collectionName']
        self.url = json.get('collectionViewUrl', None)
        self.amg_id = json.get('amgAlbumId', None)

        self.price = round(json['collectionPrice'] or 0, 4)
        self.price_currency = json['currency']
        self.track_count = json['trackCount']
        self.copyright = json.get('copyright', None)

        self._set_artist(json)

    def _set_artist(self, json):
        self.artist = None
        if json.get('artistId'):
            id = json['artistId']
            self.artist = Artist(id)
            self.artist._set(json)


class Track(Resource):
    """The Track :class:`Resource` represents a single track from the iTunes
    store
    """

    def _set(self, json):
        super(Track, self)._set(json)
        # Track information
        self.name = json['trackName']
        self.url = json.get('trackViewUrl', None)
        self.preview_url = json.get('previewUrl', None)
        self.price = None
        if 'trackPrice' in json and json['trackPrice'] is not None:
            self.price = round(json['trackPrice'], 4)
        self.number = json.get('trackNumber', None)
        self.duration = None
        if 'trackTimeMillis' in json and json['trackTimeMillis'] is not None:
            self.duration = round(json.get('trackTimeMillis', 0.0)/1000.0, 2)
        try:
            self._set_artist(json)
        except KeyError:
            self.artist = None
        try:
            self._set_album(json)
        except KeyError:
            self.album = None

    def _set_artist(self, json):
        self.artist = None
        if json.get('artistId'):
            id = json['artistId']
            self.artist = Artist(id)
            self.artist._set(json)

    def _set_album(self, json):
        if 'collectionId' in json:
            id = json['collectionId']
            self.album = Album(id)
            self.album._set(json)


class Audiobook(Album):
    """The Audiobook :class:`Resource` represents an iTunes Audiobook"""


class Software(Track):
    """The Software :class:`Resource` represents an iTunes App resource"""
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.ratings = dict(avg=dict(current=None, all=None),
                            num=dict(current=None, all=None))

    def _set(self, json):
        super(Software, self)._set(json)
        self.version = json.get('version', None)
        self.price = json.get('price', None)
        self.description = json.get('description', None)
        self.screenshots = json.get('screenshotUrls', None)
        self.genres = json.get('genres', None)
        self.seller_url = json.get('sellerUrl', None)
        self.languages = json.get('languageCodesISO2A', None)
        self.file_size_bytes = json.get('fileSizeBytes', 0)
        self.bundle_id = json.get('bundleId', None)
        self.release_notes = json.get('releaseNotes', None)
        self.primary_genre_id = json.get('primaryGenreId', 0)

        self._set_ratings(json)
        self._set_current_version_release_date(json)

    def _set_ratings(self, json):
        k = 'averageUserRatingForCurrentVersion'
        self.ratings['avg']['current'] = json.get(k, None)
        self.ratings['avg']['all'] = json.get('averageUserRating', None)
        k = 'userRatingCountForCurrentVersion'
        self.ratings['num']['current'] = json.get(k, None)
        self.ratings['num']['all'] = json.get('userRatingCount', None)

    def _set_current_version_release_date(self, json):
        self.current_version_release_date = None
        if 'currentVersionReleaseDate' in json and json['currentVersionReleaseDate']:
            self.current_version_release_date = datetime.strptime(json['currentVersionReleaseDate'], TS_FORMAT)


class TVEpisode(Track):
    """The TVEpisode :class:`Resource` represents a track type that represents
    a single TV Episode.
    """

    def _set(self, json):
        super(TVEpisode, self)._set(json)
        self.content_rating = json.get('contentAdvisoryRating', None)
        self.short_description = json.get('shortDescription', None)
        self.long_description = json.get('longDescription', None)
        self.explicitness = json.get('trackExplicitness', None)

        self.episode_number = json.get('trackNumber', None)
        self.genre = json.get('primaryGenreName', None)
        self.episode_id = json.get('trackId', None)
        self.show_id = json.get('artistId', None)
        self.season = json.get('collectionName', None)[-1:]
        self.season_id = json.get('collectionId', None)


class Lookup(BaseObject):
    """A data model for an individual resource look up against iTunes"""
    resource = 'lookup'

    def __init__(self, id, entity=None, limit=50):
        super(self.__class__, self).__init__(id=id, entity=entity, limit=limit)
        self.id = id


def lookup(id):
    """Perform an individual :class:`Lookup` on a single resource in the iTunes
    Store API
    """
    items = Lookup(id).get()
    if not items:
        raise NoResultsFoundException()
    return items[0]


class LookupUPC(BaseObject):
    """A data model for an individual resource look up against iTunes"""
    resource = 'lookup'

    def __init__(self, upc, entity=None, limit=50):
        super(self.__class__, self).__init__(upc=upc, entity=entity, limit=limit)
        self.upc = upc


def lookup_upc(upc):
    """Perform an individual :class:`LookupUPC` on a single resource in the iTunes
    Store API
    """
    items = LookupUPC(upc).get()
    if not items:
        raise NoResultsFoundException()
    return items[0]
