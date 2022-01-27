#!/usr/bin/env python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union

import pydantic
import requests
from bs4 import BeautifulSoup


class TextBody(pydantic.BaseModel):
    """ Blog body data format.
    """
    url: str
    title: str
    date: str
    extra_url: Optional[str] = None
    tag: Optional[str] = None
    author: Optional[str] = None

    def __str__(self) -> str:
        str_ = ""
        for key, value in self.__dict__.items():
            str_ += f"{key}: {value}\n"
        return str_


class UrlParser(ABC):
    def __init__(self, url: str, host: str, name: str) -> None:
        self.url = url
        self.host = host
        self.name = name
        self.entry_point = None
        self.results = {}
        self.spider = requests.Session()
        self.spider.encoding = 'utf-8'
        self.spider.headers.update({
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        })

    def fetch_soup(self) -> BeautifulSoup:
        """Return a BeautifulSoup object.
        """
        response = self.spider.get(self.url)
        return BeautifulSoup(response.content, 'html.parser')

    @abstractmethod
    def parse(
        self, soup: BeautifulSoup
    ) -> Dict[str, Union[str, Dict[str, str], List[str]]]:
        """Return a list of tuples, each tuple contains a url and a title.
        """
        pass

    def __str__(self) -> str:
        return f'\
            \n class_name: {self.__class__.__name__}\
            \n url: {self.url}\
            \n host: {self.host}\
            \n results: {self.results}'
