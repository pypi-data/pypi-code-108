from typing import List, Dict, Union

import requests

TRecord = Dict[str, Union[str, int]]
TStringFilter = Union[str, List[str], None, Dict[str, Union[str, List[str], None]]]
TIntFilter = Union[int, List[int], None, Dict[str, Union[int, List[int], None]]]
TSortFilter = Dict[str, str]
TDebugHTTPResponse = Union[requests.Response, List[requests.Response]]
