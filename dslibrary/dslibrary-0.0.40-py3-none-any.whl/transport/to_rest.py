"""
Implementation of dslibrary that makes REST calls.
"""
import json
import re
import io
import time

try:
    import requests
except ImportError:
    requests = None

from ..exceptions import DSLibraryException, DSLibraryCommunicationError
from ..metadata import Metadata
from ..front import DSLibrary
from ..utils import filechunker
from ..utils import dbconn


PTN_MODE = re.compile(r'^[rwa]b?$')


class DSLibraryViaREST(DSLibrary):
    """
    A model can send all its dslibrary requests over REST and have them handled elsewhere.
    """
    def __init__(self, url: str, token=None, spec: dict=None, auth_header_name: str="X-DSLibrary-Token"):
        super(DSLibraryViaREST, self).__init__(spec=spec)
        if not url.endswith("/"):
            url += "/"
        self._url = url
        self._headers = {auth_header_name: token} if token else {}
        self._session = requests.session() if requests else None
        self._meta = None
        self._context = None
        self._timeouts = (90, 10)

    def _do_comm(self, method: str, path: str, params: dict=None, data=None, as_json: bool=True):
        """
        All HTTP communication goes through here.
        """
        if not self._session:
            # TODO let's use urllib instead of requests when requests is not available
            raise DSLibraryException("The 'requests' package is required to use dslibrary in this mode.")
        try:
            resp = self._session.request(
                method, self._url + path, params=params, data=data, headers=self._headers, timeout=self._timeouts
            )
            resp.raise_for_status()
        except requests.exceptions.RequestException as err:
            raise DSLibraryCommunicationError(*err.args)
        if as_json:
            try:
                return resp.json()
            except ValueError as err:
                raise DSLibraryCommunicationError(f"JSON encoding error: {err}")
        return resp

    def _fetch_context(self):
        if self._context is None:
            self._context = self._do_comm("get", "context") or {}

    def get_metadata(self) -> Metadata:
        """
        Metadata can be supplied by the remote endpoint.  We could check for local metadata here, but it gives the
        remote controller more flexibility if we let it be in charge of this.
        """
        if not self._meta:
            self._fetch_context()
            self._meta = Metadata(**self._context.get("metadata") or {})
        return self._meta

    def get_parameters(self):
        """
        All the processing of parameters is delegated to the remote.
        """
        self._fetch_context()
        return self._context.get("parameters") or {}

    def _open_stream(self, category: str, url: str, mode: str, filename: str=None, params: dict=None, chunk_size=5000000):
        """
        General purpose read/write file streams over HTTP.
        """
        if not PTN_MODE.match(mode):
            raise ValueError("invalid mode: %s" % mode)
        if "r" in mode:
            def read_chunk(start, end):
                resp = self._do_comm("get", category, params={"resource_name": url, "byte_range": json.dumps([start, end]), **(params or {})}, as_json=False)
                return resp.content if "b" in mode else resp.text
            return filechunker.ChunkedFileReader(filename, reader=read_chunk, mode=mode, chunk_size=chunk_size)
        else:
            def write_chunk(content, append, hint=None):
                if ("b" in mode) == isinstance(content, str):
                    raise TypeError("incorrect data type for mode=%s" % mode)
                resp = self._do_comm("put", category, params={"resource_name": url, "append": append, "hint": hint}, data=content)
                return resp.get("upload_id")
            return filechunker.ChunkedFileWriter(filename, writer=write_chunk, mode=mode)

    def _opener(self, path: str, mode: str, **kwargs) -> io.IOBase:
        return self._open_stream("resources", path, mode, filename=path)

    def open_run_data(self, filename: str, mode: str='rb') -> io.RawIOBase:
        """
        Shared pipeline data has a different endpoint.
        """
        return self._open_stream("run_data", filename, mode, filename=filename)

    def next_scoring_request(self, timeout: float=None) -> (dict, None):
        """
        Scoring requests come from a remote endpoint.
        """
        timeout = timeout or 60
        t_timeout = time.time() + timeout
        interval = min(10, timeout/3)
        while True:
            resp = self._do_comm("get", "scoring-requests", params={"timeout": interval}, as_json=True)
            if resp.get("shutdown"):
                raise StopIteration
            if "request" in resp:
                return resp["request"] or {}
            if time.time() > t_timeout:
                return

    def send_score(self, score):
        """
        Scoring responses go to a remote endpoint.
        """
        self._do_comm("post", "score", params={"value": score})

    def get_sql_connection(self, resource_name: str, for_write: bool=False, **kwargs):
        """
        SQL conversation is 'chunked across REST', so to speak.
        """
        if not isinstance(resource_name, str):
            raise ValueError(f"get_db_connection(): expected str for 'connection_name', got {type(resource_name)}")
        params = dict(resource_name=resource_name)

        def read(operation, parameters):
            # FIXME re-establish this upstream
            '''
            # pandas makes this specific query to verify a table does not already exist (pandas.DataFrame.to_sql())
            if "select name from sqlite_master" in operation.lower():
                # convert to standard SQL
                operation = "select distinct table_name as name from INFORMATION_SCHEMA.TABLES where table_name=?"
                # try to qualify based on database
                if database:
                    operation += f" and table_schema='{database}'"
            '''
            resp = self._do_comm(
                "get", "db", params=dict(**params, sql=operation, parameters=json.dumps(parameters))
            )
            cols = resp[0]
            rows = resp[1:]
            more = None
            if rows and isinstance(rows[-1], str):
                more = rows.pop(-1)
            descr = [[col, None, None, None, None, None] for col in cols]
            return descr, rows, more

        def read_more(chunk):
            resp = None
            for _ in range(15):
                resp = self._do_comm("get", "db", params=dict(**params, more=chunk, max_wait=60))
                if resp:
                    break
            if not resp:
                raise DSLibraryCommunicationError("timeout waiting for results")
            rows = resp[1:]
            more = None
            if rows and isinstance(rows[-1], str):
                more = rows.pop(-1)
            return rows, more

        def write(operation, parameters):
            self._do_comm("post", "db", data=dict(**params, sql=operation, parameters=parameters))

        return dbconn.Connection(read, write if for_write else None, read_more=read_more)
