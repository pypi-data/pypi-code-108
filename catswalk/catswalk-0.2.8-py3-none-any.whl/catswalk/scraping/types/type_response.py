from dataclasses import dataclass
from typing import List, Mapping
from bs4 import BeautifulSoup
import json
from requests import Response as R
import logging

logger = logging.getLogger()

@dataclass
class Response:
    """[summary]
    """
    headers: Mapping[str, str]
    content: str
    response: R

@dataclass
class ResponseHtml:
    """[summary]
    """
    headers: Mapping[str, str]
    content: BeautifulSoup
    response: R

@dataclass
class ResponseJson:
    """[summary]
    """
    headers: Mapping[str, str]
    content:  json
    response: R