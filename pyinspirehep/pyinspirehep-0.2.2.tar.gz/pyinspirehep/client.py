"""Client to use Inspirehep API.

The client.py moducle contains the base class `Client` which can be used to
get data from Inspirehep API.

"""

import requests
from pyinspirehep.exception import (
    InspirehepPIDDoesNotExistError,
    InspirehepTooManyRequestsError,
)
import time
from pyinspirehep.data_models import SingleRecordResponse


class Client:
    """Client to use Inspirehep API.
    """

    REST_API_URL = 'https://inspirehep.net/api/'

    SEARCH_RESULT_KEY = 'hits'

    IDENTIFIER_TYPES = [
        'literature',
        'authors',
        'institutions',
        'conferences',
        'seminars',
        'journals',
        'jobs',
        'experiments',
        'data',
        ]

    EXTERNAL_IDENTIFIER_TYPES = [
        'doi',
        'arxiv',
        'orcid',
        ]

    LIMIT_TIME = 5

    PAGINATION_LIMIT = 10000

    MAX_RECORDS_PER_PAGE = 1000

    MAX_PAGES = PAGINATION_LIMIT // MAX_RECORDS_PER_PAGE
    

    def __init__(self) -> None:
        self.session = self._init_session()

    def _init_session(self) -> requests.session:
        """Initialize session.
        """

        session = requests.session()
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'pyinspirehep',
            'Content-Type': 'application/json',
            }
        session.headers.update(headers)
        return session

    def wait_429(self) -> None:
        """Wait before sending next request.

        Use to wait `LIMIT_TIME` seconds before sending new requests.
        """
        time.sleep(self.LIMIT_TIME)

    def _get(self, *args, **kwargs) -> dict:
        """Sends a GET request and returns json data.

        This method uses `requests.get` method to get data from API and
        and returns data as json.

        Parameters
        ----------
        *args :
            Passed to `requests.get` as *args.
            
        **kwargs :
            Passed to `requests.get` as **kwargs.

        Returns
        -------
        dict
            Result of json data will be returned as Python dict.

        Raises
        ------
        InspirehepPIDDoesNotExistError
            When the requested object was not found.

        InspirehepTooManyRequestsError
            When because of too many request the IP is blocked for
            a few seconds.

        """
        try:
            response = requests.get(*args, **kwargs)
        except requests.exceptions.ConnectionError as e:
            raise InspirehepTooManyRequestsError(str(e))
        data = response.json()
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise InspirehepPIDDoesNotExistError(
                data.get('message', '404 status code'),
                )
        elif response.status_code == 429:
            raise InspirehepTooManyRequestsError(
                data.get('message', '429 status code'),
                )

    def _get_record(
        self,
        *args,
        identifier_type: str,
        identifier_value: str,
        ) -> dict:
        """

        Parameters
        ----------
        identifier_type : str
            The `identifier-value` type is a string which determines
            what type of object to be get. For example, it can be
            'authors', 'literature', etc.

        identifier_value : str
            The `identifier-value` is a number identifying the given record
            in the INSPIRE database (also called record ID or recid)

        *args :
            The fields that must be included in metadata. If not specified, 
            all possible fields in metadata will be send in response.


        Returns
        -------
        dict
            The json data part of the respone as Python dict will be returned.

        """
        args = [self.REST_API_URL, identifier_type, identifier_value]
        fields = ""
        if args:
            fields = ",".join(args)
        if fields:
            return self._get(
                Client._create_uri(*args),
                params={'fields':fields}
                )
        else:
            return self._get(
                Client._create_uri(*args)
                )

    def _create_q(
        metadata_field: str,
        nested_key: str = None,
        value: str = "",
        ) -> str:
        """Creates query to use in URL for a field

        Parameters
        ----------
        metadata_field : str
            
        nested_key : str
             (Default value = None)
        value : str
             (Default value = "")

        Returns
        -------
        str

        """
        if nested_key is None:
            return f"{metadata_field}:{value}"
        else:
            return f"{metadata_field}.{nested_key}:{value}"

    def _search(
        self,
        *args,
        identifier_type: str,
        **kwargs,
        ) -> dict:
        """

        Parameters
        ----------
        *args :
            The fields that must be included in metadata. If not specified, 
            all possible fields in metadata will be send in response. All
            items in the *args must be string. Using `Client._create_params`
            all items in *args will be concatenated and will be the value for
            fields key in query parameters in request URL.
            
        identifier_type : str
            
        **kwargs :
            Keyworod arguments will be passed to `Client._create_params` and 
            they will created values for query parameters such as size, page,
            sort and q.
            

        Returns
        -------

        """
        uri_args = [self.REST_API_URL, identifier_type]
        return self._get(
            Client._create_uri(*uri_args),
            params=Client._create_params(*args, **kwargs),
            )

    def _get_record_object(
        self,
        *args,
        identifier_type: str,
        identifier_value: str,
        ) -> SingleRecordResponse:
        """

        Parameters
        ----------
        *args:
            The fields that must be included in metadata.

        identifier_type : str
            
        identifier_value : str
            

        Returns
        -------
        SingleRecrodResponse

        """
        return SingleRecordResponse.from_response(
            self._get_record(
                *args,
                identifier_type=identifier_type,
                identifier_value=identifier_value,
                ),
            )

    @staticmethod
    def _create_params(
        *args,
        sorting: str = None,
        page: str = None,
        size: str = None,
        q: str = None,
        ) -> dict:
        """

        Parameters
        ----------
        *args:
            All items in *args must be string. The positional arguments in
            args will be used as filters of fields of metadata. If no
            positional arugemnt was provided, then all fields of metadata
            will be returned in result of the response.

        sorting : str
            (Default value = None). Determines the sort roder of objects
            in response.

        page : str
            (Default value = None). The page number to get in query.

        size : str
            (Default value = None). The number of records in page.

        q : str
            (Default value = None). The search query.

        Returns
        -------
        dict

        >>> client = Client()
        >>> client._create_params('name.value', 'positions', sorting='bestmatch', size=1000, page=1)
        {'sort': 'bestmatch', 'page': 1, 'size': 1000, 'fields': 'name.value,positions'}
        >>> client._create_params('name.value', 'positions', sorting='bestmatch', size=1000, page=1, q='control_number:1966745')
        {'sort': 'bestmatch', 'page': 1, 'size': 1000, 'q': 'control_number:1966745', 'fields': 'name.value,positions'}
        """
        params = {}
        if sorting is not None:
            params['sort'] = sorting  # The sort order
        if page is not None:
            params['page'] = page  # The page number
        if size is not None:
            params['size'] = size  # The number of results returned per page
        if q is not None:
            params['q'] = q  # The search query
        fields = None  # The fields in the metadata to be returned
        if args:
            fields = ",".join(args)
        if fields:
            params['fields'] = fields

        return params

    @staticmethod
    def _create_uri(*args, end: str = "") -> str:
        """

        Parameters
        ----------
        *args :
            
        end : str
            (Default value = "")

        Returns
        -------
        str

        """
        assert end in ("", "/")
        return "/".join(args) + end

    def get_literature(
        self,
        literature_id: str,
        *args,
        ) -> dict:
        """

        Parameters
        ----------
        literature_id : str

        *args :
            Items to include in metadata.
            

        Returns
        -------
        dict


        >>> client = Client()
        >>> paper = client.get_literature("451647")
        >>> paper["metadata"]["titles"][0]["title"]
        'The Large N limit of superconformal field theories and supergravity'
        """
        return self._get_record(
            *args,
            identifier_type='literature',
            identifier_value=literature_id,
            )

    def get_literature_object(
        self,
        literature_id: str,
        *args,
        ) -> SingleRecordResponse:
        """

        Parameters
        ----------
        literature_id : str

        *args :
            Items to include in metadata.            

        Returns
        -------
        SingleRecordResponse

        """
        return self._get_record_object(
            *args,
            identifier_type='literature',
            identifier_value=literature_id,
            )

    def get_author(
        self,
        author_id: str,
        *args,
        ) -> dict:
        """

        Parameters
        ----------
        author_id : str

        *args :
            Items to include in metadata.

        Returns
        -------
        dict

        """
        return self._get_record(
            *args,
            identifier_type='authors',
            identifier_value=author_id,
            )

    def get_author_object(
        self,
        author_id: str,
        *args,
        ) -> SingleRecordResponse:
        """

        Parameters
        ----------
        author_id : str

        *args :
            Items to include in metadata.
            

        Returns
        -------
        SingleRecordResponse

        """
        return self._get_record_object(
            *args,
            identifier_type='authors',
            identifier_value=author_id,
        )

    def search_authors(
        self,
        *args,
        sorting='bestmatch',
        size=1000,
        page=1,
        q=None,
        name=None,
        ) -> dict:
        """

        Parameters
        ----------
        sorting :
             (Default value = 'bestmatch')
        size :
             (Default value = 1)
        page :
             (Default value = 1)
        fields:
            (Default value = None)
        q :
             (Default value = None)
        name :
             (Default value = None)

        Returns
        -------
        dict

        """
        if name is not None:
            q = Client._create_q('name', 'value', name)
        return self._search(
            *args,
            identifier_type='authors',
            sorting=sorting,
            size=size,
            page=page,
            q=q,
            )

    def get_institution(
        self,
        institution_id: str,
        *args,
        ) -> dict:
        """

        Parameters
        ----------
        institution_id : str
            

        Returns
        -------
        dict

        """
        return self._get_record(
            *args,
            identifier_type='institutions',
            identifier_value=institution_id,
            )

    def get_institution_object(
        self,
        institution_id: str,
        *args,
        ) -> SingleRecordResponse:
        """

        Parameters
        ----------
        institution_id : str
            

        Returns
        -------
        SingleRecordResponse

        """
        return self._get_record_object(
            *args,
            identifier_type='institutions',
            identifier_value=institution_id,
            )

    def get_conference(
        self,
        conference_id: str,
        *args,
        ) -> dict:
        """

        Parameters
        ----------
        conference_id : str
            

        Returns
        -------
        dict

        """
        return self._get_record(
            *args,
            identifier_type='conferences',
            identifier_value=conference_id,
            )

    def get_conference_object(
        self,
        conference_id: str,
        *args,
        ) -> SingleRecordResponse:
        """

        Parameters
        ----------
        conference_id : str
            

        Returns
        -------
        SingleRecordResponse

        """
        return self._get_record_object(
            *args,
            identifier_type='conferences',
            identifier_value=conference_id,
        )

    def get_seminar(
        self,
        seminar_id: str,
        *args,
        ) -> dict:
        """

        Parameters
        ----------
        seminar_id : str
            

        Returns
        -------
        dict

        """
        return self._get_record(
            *args,
            identifier_type='seminars',
            identifier_value=seminar_id,
            )

    def get_seminar_object(
        self,
        seminar_id: str,
        *args,
        ) -> SingleRecordResponse:
        """

        Parameters
        ----------
        seminar_id : str
            

        Returns
        -------
        SingleRecordResponse

        """
        return self._get_record_object(
            *args,
            identifier_type='seminars',
            identifier_value=seminar_id,
        )

    def get_journal(
        self,
        journal_id: str,
        *args,
        ) -> dict:
        """

        Parameters
        ----------
        journal_id : str
            

        Returns
        -------
        dict

        """
        return self._get_record(
            *args,
            identifier_type='journals',
            identifier_value=journal_id,
            )

    def get_journal_object(
        self,
        journal_id: str,
        *args,
        ) -> SingleRecordResponse:
        """

        Parameters
        ----------
        journal_id : str
            

        Returns
        -------
        SingleRecordResponse

        """
        return self._get_record_object(
            *args,
            identifier_type='journals',
            identifier_value=journal_id,
        )

    def get_job(
        self,
        job_id: str,
        *args,
        ) -> dict:
        """

        Parameters
        ----------
        job_id : str
            

        Returns
        -------
        dict

        """
        return self._get_record(
            *args,
            identifier_type='jobs',
            identifier_value=job_id,
            )

    def get_job_object(
        self,
        job_id: str,
        *args,
        ) -> SingleRecordResponse:
        """

        Parameters
        ----------
        job_id : str
            

        Returns
        -------
        SingleRecordResponse

        """
        return self._get_record_object(
            *args,
            identifier_type='jobs',
            identifier_value=job_id,
        )

    def get_experiment(
        self,
        experiment_id: str,
        *args,
        ) -> dict:
        """

        Parameters
        ----------
        experiment_id : str
            

        Returns
        -------
        dict

        """
        return self._get_record(
            *args,
            identifier_type='experiments',
            identifier_value=experiment_id,
            )

    def get_experiment_object(
        self,
        experiment_id: str,
        *args,
        ) -> SingleRecordResponse:
        """

        Parameters
        ----------
        experiment_id : str
            

        Returns
        -------
        SingleRecordResponse

        """
        return self._get_record_object(
            *args,
            identifier_type='experiments',
            identifier_value=experiment_id,
        )

    def get_data(
        self,
        data_id: str,
        *args,
        ) -> dict:
        """

        Parameters
        ----------
        data_id : str
            

        Returns
        -------
        dict

        """
        return self._get_record(
            *args,
            identifier_type='data',
            identifier_value=data_id,
            )

    def get_data_object(
        self,
        data_id: str,
        *args,
        ) -> dict:
        """

        Parameters
        ----------
        data_id : str
            

        Returns
        -------
        SingleRecordResponse

        """
        return self._get_record_object(
            *args,
            identifier_type='data',
            identifier_value=data_id,
        )

    def get_doi(
        self,
        doi_identifier: str,
        *args,
        ) -> dict:
        """

        Parameters
        ----------
        doi_identifier : str
            

        Returns
        -------
        dict

        >>> client = Client()
        >>> literature_record = client.get_doi("10.1103/PhysRevLett.19.1264")
        >>> literature_record["metadata"]["titles"][-1]["title"]
        'A Model of Leptons'
        """
        return self._get_record(
            *args,
            identifier_type='doi',
            identifier_value=doi_identifier,
            )

    def get_doi_object(
        self,
        doi_identifier: str,
        *args,
        ) -> SingleRecordResponse:
        """

        Parameters
        ----------
        doi_identifier : str
            

        Returns
        -------
        SingleRecordResponse

        """
        return self._get_record_object(
            *args,
            identifier_type='doi',
            identifier_value=doi_identifier,
        )

    def get_arxiv(
        self,
        arxiv_identifier: str,
        *args,
        ) -> dict:
        """

        Parameters
        ----------
        arxiv_identifier : str
            

        Returns
        -------
        dict

        >>> client = Client()
        >>> literature_record = client.get_arxiv("1207.7214")
        >>> literature_record["metadata"]['titles'][-1]['title']
        'Observation of a new particle in the search for the Standard Model Higgs boson with the ATLAS detector at the LHC'
        >>> literature_record["metadata"]['titles'][-1]['source']
        'arXiv'
        >>> literature_record = client.get_arxiv("hep-ph/0603175")
        >>> literature_record["metadata"]['titles'][-1]['source']
        'arXiv'
        """
        return self._get_record(
            *args,
            identifier_type='arxiv',
            identifier_value=arxiv_identifier,
            )

    def get_arxiv_object(
        self,
        arxiv_identifier: str,
        *args,
        ) -> dict:
        """

        Parameters
        ----------
        arxiv_identifier : str
            

        Returns
        -------
        SingleRecordResponse
        
        """
        return self._get_record_object(
            *args,
            identifier_type='arxiv',
            identifier_value=arxiv_identifier,
            )

    def get_orcid(
        self,
        orcid_id: str,
        *args,
        ) -> dict:
        """

        Parameters
        ----------
        orcid_id : str
            

        Returns
        -------
        dict


        >>> client = Client()
        >>> author_record = client.get_orcid("0000-0003-3897-046X")
        >>> author_record["metadata"]["name"]["value"]
        'Seiberg, Nathan'
        """
        return self._get_record(
            *args,
            identifier_type='orcid',
            identifier_value=orcid_id,
            )

    def get_orcid_object(
        self,
        orcid_id: str,
        *args,
        ) -> SingleRecordResponse:
        """

        Parameters
        ----------
        orcid_id : str
            

        Returns
        -------
        SingleRecordResponse

        """
        return self._get_record_object(
            *args,
            identifier_type='orcid',
            identifier_value=orcid_id,
        )


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
