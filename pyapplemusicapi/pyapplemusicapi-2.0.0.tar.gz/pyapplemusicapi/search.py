# -*- coding: utf-8 -*-
"""This module contains utilities for performing a variety of different
searches against the iTunes Store API
"""

from pyapplemusicapi import COUNTRY, API_VERSION, BaseObject

__all__ = ['search_track', 'search_album', 'search_artist', 'search_app',
           'search_episode', 'search_season', 'search', 'search_movie',
           'Search']


def search_track(query, limit=100, offset=0, order=None, store=COUNTRY):
    """Search for a track resource

    :param query: The query to perform against the iTunes store API
    :param limit: The max number of responses to return. Default: 100
    :param offset: The offset into a collection of resources. Default: 0
    :param order: The key to order a collection of resources by. Possible
        values are 'rank' or 'popular.' Default: :const:`None`
    :param store: The iTunes store localization to search against.
        Default: `COUNTRY`
    """
    return Search(query=query, media='music', entity='song',
                  offset=offset, limit=limit, order=order, country=store).get()


def search_album(query, limit=100, offset=0, order=None, store=COUNTRY):
    """Search for an album resource

    :param query: The query to perform against the iTunes store API
    :param limit: The max number of responses to return. Default: 100
    :param offset: The offset into a collection of resources. Default: 0
    :param order: The key to order a collection of resources by. Possible
        values are 'rank' or 'popular.' Default: :const:`None`
    :param store: The iTunes store localization to search against.
        Default: `COUNTRY`
    """
    return Search(query=query, media='music', entity='album',
                  limit=limit, offset=offset, order=order, country=store).get()


def search_artist(query, limit=100, offset=0, order=None, store=COUNTRY):
    """Search for an artist resource

    :param query: The query to perform against the iTunes store API
    :param limit: The max number of responses to return. Default: 100
    :param offset: The offset into a collection of resources. Default: 0
    :param order: The key to order a collection of resources by. Possible
        values are 'rank' or 'popular.' Default: :const:`None`
    :param store: The iTunes store localization to search against.
        Default: `COUNTRY`
    """
    return Search(query=query, media='music', entity='musicArtist',
                  limit=limit, offset=offset, order=order, country=store).get()


def search_app(query, limit=100, offset=0, order=None, store=COUNTRY):
    """Search for an app resource

    :param query: The query to perform against the iTunes store API
    :param limit: The max number of responses to return. Default: 100
    :param offset: The offset into a collection of resources. Default: 0
    :param order: The key to order a collection of resources by. Possible
        values are 'rank' or 'popular.' Default: :const:`None`
    :param store: The iTunes store localization to search against.
        Default: `COUNTRY`
    """
    return Search(query=query, media='software', limit=limit,
                  offset=offset, order=order, country=store).get()


def search_episode(query, limit=100, offset=0, order=None, store=COUNTRY):
    """Search for a TV Episode resource

    :param query: The query to perform against the iTunes store API
    :param limit: The max number of responses to return. Default: 100
    :param offset: The offset into a collection of resources. Default: 0
    :param order: The key to order a collection of resources by. Possible
        values are 'rank' or 'popular.' Default: :const:`None`
    :param store: The iTunes store localization to search against.
        Default: `COUNTRY`
    """
    return Search(query=query, media='tvShow', entity='tvEpisode',
                  limit=limit, offset=offset, order=order, country=store).get()


def search_season(query, limit=100, offset=0, order=None, store=COUNTRY):
    """Search for a TV Season resource

    :param query: The query to perform against the iTunes store API
    :param limit: The max number of responses to return. Default: 100
    :param offset: The offset into a collection of resources. Default: 0
    :param order: The key to order a collection of resources by. Possible
        values are 'rank' or 'popular.' Default: :const:`None`
    :param store: The iTunes store localization to search against.
        Default: `COUNTRY`
    """
    return Search(query=query, media='tvShow', entity='tvSeason',
                  limit=limit, offset=offset, order=order, country=store).get()


def search(query, media='all', limit=100, offset=0, order=None, store=COUNTRY):
    """Search for any type of resource

    :param query: The query to perform against the iTunes store API
    :param limit: The max number of responses to return. Default: 100
    :param offset: The offset into a collection of resources. Default: 0
    :param order: The key to order a collection of resources by. Possible
        values are 'rank' or 'popular.' Default: :const:`None`
    :param store: The iTunes store localization to search against.
        Default: `COUNTRY`
    """
    return Search(query=query, media=media, limit=limit,
                  offset=offset, order=order, country=store).get()


def search_movie(query, limit=100, offset=0, order=None, store=COUNTRY):
    """Search for a Movie resource

    :param query: The query to perform against the iTunes store API
    :param limit: The max number of responses to return. Default: 100
    :param offset: The offset into a collection of resources. Default: 0
    :param order: The key to order a collection of resources by. Possible
        values are 'rank' or 'popular.' Default: :const:`None`
    :param store: The iTunes store localization to search against.
        Default: `COUNTRY`
    """
    return Search(query=query, media='muovie', entity='movie',
                  offset=offset, limit=limit, order=order, country=store).get()


class Search(BaseObject):
    """Search iTunes Store for a variety of different resource types"""
    resource = 'search'

    def __init__(self, query, country=COUNTRY, media='all', entity=None,
                 attribute=None, offset=0, limit=50, order=None,
                 lang='en_us', version=API_VERSION, explicit='Yes'):
        """
        :param query: The query to perform against the iTunes store API
        :param country: The iTunes store localization to search against.
            Default: `COUNTRY`
        :param media: The media type to search for. Default: 'all'
        :param entity: A specialized form of `media` to search for.
        :param limit: The max number of responses to return. Default: 100
        :param offset: The offset into a collection of resources. Default: 0
        :param order: The key to order a collection of resources by. Possible
            values are 'rank' or 'popular.' Default: :const:`None`
        :param lang: The preferred language to see search results in.
            Default: 'en_us'
        :param version: The iTunes store API version to access.
            Default: `API_VERSION`
        :param explicit: Allow resources flagged as 'explicit' to be returned
            in the search results. Default: 'Yes'
        """
        super(self.__class__, self).__init__(term=query, country=country,
                                             media=media, entity=entity,
                                             attribute=attribute, limit=limit,
                                             offset=offset, order=order,
                                             lang=lang, version=version,
                                             explicit=explicit)
