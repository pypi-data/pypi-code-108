# -*- coding: utf-8 -*-
# Copyright © 2021 Wacom. All rights reserved.
from http import HTTPStatus
from typing import Dict, Any

import requests
from requests import Response

from knowledge import logger
from knowledge.base.entity import LanguageCode


class ExtractionException(Exception):
    pass


def __extract_abstract__(title: str, language: str = 'en') -> str:
    """Extracting an abstract.

    Parameters
    ----------
    title: str -
        Title of wikipedia article
    language: str -
        language_code of Wikipedia

    Returns
    -------
    abstract: str
        Abstract of the wikipedia article
    """
    params: Dict[str, str] = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "extracts",
        "exintro": "1",
        "explaintext": "1",
        "redirects": "1"
    }

    url: str = f'https://{language}.wikipedia.org/w/api.php'
    response: Response = requests.get(url, params=params)
    if response.status_code == HTTPStatus.OK:
        result: Dict[str, Any] = response.json()
        if 'query' in result:
            pages = result['query']['pages']
            if len(pages) == 1:
                for v in pages.values():
                    return v.get('extract', '')
    raise ExtractionException(f"Abstract for article with {title} in language_code {language} cannot be extracted.")


def __extract_thumb__(title: str, language: str = 'en') -> str:
    """
    Extracting thumbnail from Wikipedia.

    Parameters
    ----------
    title: str
        Title of wikipedia article
    language: LanguageCode
        Language code of Wikipedia

    Returns
    -------
    url: str
        thumb URL
    """
    params: Dict[str, str] = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "pageimages",
        "pithumbsize": "400"
    }

    url: str = f'https://{language}.wikipedia.org/w/api.php'
    response: Response = requests.get(url, params=params)
    if response.ok:
        result: dict = response.json()
        try:
            if 'query' in result:
                pages: dict = result['query']['pages']
                if len(pages) == 1:
                    for v in pages.values():
                        if 'thumbnail' in v:
                            return v['thumbnail']['source']
        except Exception as e:
            logger.error(e)
    raise ExtractionException(f"Thumbnail for article with {title} in language_code {language} cannot be extracted.")


def get_wikipedia_summary(title: str, lang: str = 'en') -> Dict[str, str]:
    """
    Extracting summary image and abstract for wikipedia URL.

    Parameters
    ----------
    title: str
        Title of the Wikipedia article
    lang: str
        Language code

    Returns
    -------
    result: Dict[str, str]
        Summary dict with image and summary text
    """
    try:
        thumbnail: str = __extract_thumb__(title, lang)
    except ExtractionException as _:
        thumbnail = ''
    try:
        summary: str = __extract_abstract__(title, lang)
    except ExtractionException as _:
        summary = ''
    return {
        'summary-image': thumbnail,
        'summary-text': summary
    }


def get_wikipedia_summary_url(wiki_url: str, lang: str = 'en') -> Dict[str, str]:
    """
    Extracting summary image and abstract for wikipedia URL.
    Parameters
    ----------
    wiki_url: str
        Wikipedia URL
    lang: str
        Language code

    Returns
    -------
    result: Dict[str, str]
        Result dictionary.
    """
    title: str = wiki_url.split('/')[-1]
    return {
        'url': wiki_url,
        'summary-image': __extract_thumb__(title, lang),
        'summary-text': __extract_abstract__(title, lang)
    }
