import requests
from elasticsearch_dsl import Search
from elasticsearch_dsl.response import Response
from typing import List, Tuple
from minetext.config import Config
from minetext.domain.es_request import EsRequest
from minetext.identifiers import Identifiers


class Mine:
    _host: str
    _es_request: EsRequest
    _internal_token: str

    def __init__(self, es_request: EsRequest, host: str = Config.host, internal_token: str = None):
        """
        Initialize the MINE object.

        :param host: the endpoint of the REST API
        :param es_request: the object containing request information to Elasticsearch
        """
        self._host = host
        self._es_request = es_request
        self._internal_token = internal_token

    def search(self) -> Response:
        """
        Call the search endpoint with parameters provided via the ``_es_request`` property.

        :return: the result wrapped in the ``Response`` object
        """
        url = f'{self._host}/search'

        payload = {
            'q': self._es_request.search_term,
            'f[]': self._es_request.filters,
            'a': self._es_request.aggregation,
            'p': self._es_request.page,
            's': self._es_request.size,
            'wa': self._es_request.with_analytics
        }

        if self._internal_token is not None:
            headers = {
                'token': self._internal_token
            }
            result = requests.get(url, params=payload, headers=headers)
        else:
            result = requests.get(url, params=payload)

        # Parse the result using Elasticsearch Response
        response = Response(Search(), result.json())

        return response
    '''
    @staticmethod
    def get_word_count(identifiers: List[Tuple[str, List[str]]]):
        """
        Call the get_word_count endpoint with parameters provided list of identifiers tuple, which have
        work ids(doi, id) and list of file ids.

        :param identifiers: List of tuple identifiers
        :return: the result return list of identifiers, files id and total word in file
        """

        url = f'{Config.host}/search'
        payload_identifier = []

        if identifiers:
            for work_id in identifiers:
                if work_id:
                    # making lucene query string for word count search
                    # make string for work identifier on the basis of identifier string and value
                    w = f'{Identifiers.identifier_field_id}"{work_id}"'
                    #w1 = f'{Identifiers.doi}"{work_id}"'
                    # make string for file id on the base of file identifier string and value then concat every file id
                    # separated by OR operator
                    #f = '({0})'.format(" OR ".join([Identifiers.files_id_field + '"{0}"'.format(w) for w in file_id]))
                    # concat work id and file id separated by AND operator
                    c = f'{w}'
                    #c1 = f'{w1}'
                    # add each string into payload_identifier list
                    payload_identifier.append(c)
                    #payload_identifier.append(c1)
        # concat each string in payload_identifier separated by OR operator
        query = " OR ".join(['({0})'.format(i) for i in payload_identifier])

        payload = {
            'q': query
        }

        result = requests.get(url, params=payload)

        # Parse the result using Elasticsearch Response
        result = Response(Search(), result.json())

        # Return only file id and word count
        response = []
        for hit in result.hits:
            words = {}
            files = hit['origin']['files']
            for file in files:
                if hasattr(file, 'word_count'):
                    for k in hit['mine']['dc_identifier']:
                        words['identifier'] = hit['mine']['dc_identifier'][k]
                        break
                    words['file_id'] = file['id']
                    words['word_count'] = file['word_count']
                    response.append(words)

        return response
    '''
    '''@staticmethod
    def get_entities(identifiers: List[Tuple[str, List[str]]]):
        """
        Call the get_entities endpoint with parameters provided list of identifiers tuple, which have
        work ids(doi, id) and list of file ids.

        :param identifiers: List of tuple identifiers

        :return: the result return list of identifiers, files id and list of topics for each file
        """
        url = f'{Config.host}/search'
        payload_identifier = []

        if identifiers:
            for work_id, file_id in identifiers:
                if work_id and file_id and ('' not in file_id):
                    # making lucene query string for topics search
                    # make string for work identifier on the basis of identifier string and value
                    w = f'{Identifiers.identifier_field_id}"{work_id}"'
                    # make string for file id on the base of file identifier string and value then concat every file id
                    # separated by OR operator
                    f = '({0})'.format(" OR ".join([Identifiers.files_id_field + '"{0}"'.format(w) for w in file_id]))
                    # concat work id and file id separated by AND operator
                    c = f'{w} AND {f}'
                    # add each string into payload_identifier list
                    payload_identifier.append(c)
        # concat each string in payload_identifier separated by OR operator
        query = " OR ".join(['({0})'.format(i) for i in payload_identifier])

        payload = {
            'q': query
        }

        result = requests.get(url, params=payload)

        # Parse the result using Elasticsearch Response
        result = Response(Search(), result.json())

        # Return only file id and word count
        response = []
        for hit in result.hits:
            topics = {}
            files = hit['origin']['files']
            for file in files:
                if hasattr(file, 'topics'):
                    for k in hit['mine']['dc_identifier']:
                        topics['identifier'] = hit['mine']['dc_identifier'][k]
                        break
                    topics['file_id'] = file['id']
                    topics['topics'] = file['topics']
                    response.append(topics)

        return response
    '''
    def get_identifiers(self) -> Response:
        """
        Call the get_identifiers endpoint

        :return: the result return list of identifiers
        """
        result = self.search()

        response = []
        for hit in result.hits:
            identifier = str
            for k in hit['mine']['dc_identifier']:
                identifier = hit['mine']['dc_identifier'][k]
                break
            response.append(identifier)

        return response

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value

    @property
    def es_request(self):
        return self._es_request

    @es_request.setter
    def es_request(self, value):
        self._es_request = value
