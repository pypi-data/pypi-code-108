from hashlib import md5
from json import loads
from pathlib import Path
from typing import Optional, Set, overload, Union

from requests import Response, post

from targer_api.constants import (
    DEFAULT_TARGER_API_URL, DEFAULT_TARGER_MODEL, DEFAULT_TARGER_MODELS
)
from targer_api.model import ArgumentSentences, ArgumentModelSentences
from targer_api.parse import parse_argument_sentences


@overload
def analyze_text(
        text: str,
        model: str = DEFAULT_TARGER_MODEL,
        api_url: str = DEFAULT_TARGER_API_URL,
        cache_dir: Optional[Path] = None,
) -> ArgumentSentences:
    pass


@overload
def analyze_text(
        text: str,
        models: Set[str],
        api_url: str = DEFAULT_TARGER_API_URL,
        cache_dir: Optional[Path] = None,
) -> ArgumentModelSentences:
    pass


def analyze_text(
        text: str,
        model_or_models: Union[str, Set[str]] = DEFAULT_TARGER_MODEL,
        api_url: str = DEFAULT_TARGER_API_URL,
        cache_dir: Optional[Path] = None,
) -> Union[ArgumentSentences, ArgumentModelSentences]:
    if isinstance(model_or_models, str):
        return _fetch_sentences_single(
            text=text,
            model=model_or_models,
            api_url=api_url,
            cache_dir=cache_dir,
        )
    else:
        return _fetch_sentences_multi(
            text=text,
            models=model_or_models,
            api_url=api_url,
            cache_dir=cache_dir,
        )


def _fetch_sentences_multi(
        text: str,
        models: Set[str] = DEFAULT_TARGER_MODELS,
        api_url: str = DEFAULT_TARGER_API_URL,
        cache_dir: Optional[Path] = None,
) -> ArgumentModelSentences:
    if cache_dir is not None:
        cache_dir.mkdir(parents=True, exist_ok=True)

    arguments: ArgumentModelSentences = {
        model: _fetch_sentences_single(
            text=text,
            model=model,
            api_url=api_url,
            cache_dir=cache_dir / model,
        )
        for model in models
    }
    return arguments


def _fetch_sentences_single(
        text: str,
        model: str = DEFAULT_TARGER_MODEL,
        api_url: str = DEFAULT_TARGER_API_URL,
        cache_dir: Optional[Path] = None,
) -> ArgumentSentences:
    content_hash: str = md5(text.encode()).hexdigest()
    cache_file = cache_dir / f"{content_hash}.json" \
        if cache_dir is not None \
        else None

    # Check if the API response is found in the cache.
    if cache_file is not None and cache_file.exists() and cache_file.is_file():
        with cache_file.open("r") as file:
            json = loads(file.read())
            return parse_argument_sentences(json)

    headers = {
        "Accept": "application/json",
        "Content-Type": "text/plain",
    }
    res: Response = post(
        api_url + model,
        headers=headers,
        data=text.encode("utf-8")
    )
    json = res.json()

    # Cache the API response.
    if cache_file is not None:
        cache_file.parent.mkdir(exist_ok=True)
        with cache_file.open("wb") as file:
            file.write(res.content)

    return parse_argument_sentences(json)
