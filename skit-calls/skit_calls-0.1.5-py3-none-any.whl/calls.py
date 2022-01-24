import asyncio
import copy
import json
import random
import tempfile
from typing import Any, Dict, Iterable, List, Optional

import aiohttp
import pandas as pd
from loguru import logger
from tqdm import tqdm

from skit_calls import constants as const


def build_call_tag_filter(reported: bool, resolved: bool) -> str:
    """
    Build a tag filter for calls.

    :param reported: Whether to filter calls that have been reported.
    :type reported: bool
    :param resolved: Whether to filter calls that have been resolved.
    :type resolved: bool
    :return: A tag filter for calls.
    :rtype: str
    """
    if reported and resolved:
        return const.ALL
    elif reported:
        return const.REPORTED
    elif resolved:
        return const.RESOLVED
    else:
        return const.ALL


def get_auth_header(token: str) -> Dict[str, str]:
    """
    Get the authorization header for the given auth token.

    :param token: An auth token.
    :type token: str
    :return: The authorization header.
    :rtype: Dict[str, str]
    """
    return {const.AUTHORIZATION: f"Bearer {token}"}


def get_full_range(current_page: int, total_pages: int) -> Iterable[int]:
    """
    Get the full range of pages to read.

    We have a paginated api to sample a subset of the calls.

    :param current_page: The current page index.
    :type current_page: int
    :param total_pages: The total number of pages.
    :type total_pages: int
    :return: A range of pages to read.
    :rtype: Iterable[int]
    """
    return range(current_page, total_pages + 1)


def get_sampled_range(
    current_page: int, total_pages: int, sample_size: int
) -> Iterable[int]:
    """
    Get a range of pages (subset) to read.

    :param current_page: The current page index.
    :type current_page: int
    :param total_pages: The total number of pages.
    :type total_pages: int
    :param sample_size: The number of calls to sample.
    :type sample_size: int
    :return: A range of pages to read.
    :rtype: Iterable[int]
    """
    return random.sample(range(current_page, total_pages + 1), sample_size)


def get_pages_to_read(
    current_page: int, total_pages: int, sample_size: int
) -> Iterable[int]:
    """
    Get a list of pages to read.

    We check if the sample size is larger than available calls.
    If we are sampling larger than the available pool then we fallback to
    the maximum number of pages.

    :param current_page: The current page index.
    :type current_page: int
    :param total_pages: The total number of pages.
    :type total_pages: int
    :param sample_size: The number of calls to sample.
    :type sample_size: int
    :return: A list of pages to read.
    :rtype: Iterable[int]
    """
    return (
        get_full_range(current_page, total_pages)
        if sample_size >= total_pages
        else get_sampled_range(current_page, total_pages, sample_size)
    )


async def inflate_call(
    session: aiohttp.ClientSession, calls_response: dict
) -> List[dict]:
    """
    Inflate a call.

    We have conversations (aka turns) that are associated with a call.
    We make requests to get all the conversations and inflate them within
    the call data structure.

    :param session: A session to use for making requests.
    :type session: aiohttp.ClientSession
    :param calls_response: A call response.
    :type calls_response: dict
    :return: A list of calls.
    :rtype: List[dict]
    """
    calls_ = calls_response.get(const.ITEMS, [])
    turns = []
    for call in calls_:
        conversations_response = await get(
            session, const.ROUTE__TURN.format(call.get(const.UUID))
        )
        conversations = copy.deepcopy(
            conversations_response.get(const.CONVERSATIONS, [])
        )

        for conversation in conversations:
            conversation_uuid = conversation.get(const.UUID)

            if not conversation_uuid:
                continue

            conversation[const.CONV_UUID] = conversation_uuid
            conversation[const.CALL_UUID] = call.get(const.UUID)
            conversation.update(**conversations_response)

            # conversation and call both are referenced by 'uuid'
            # so we created separate keys to identify them in this aggregated dataset.
            # and remove the uuid key to avoid confusion.
            del conversation[const.UUID]

            # We have aggregated conversations (moved up) with the call data, so we don't need
            # the key containing conversations anymore.
            del conversation[const.CONVERSATIONS]
            turns.append(conversation)
    return turns


async def get(
    session: aiohttp.ClientSession,
    path: str,
    params: Optional[dict] = None,
    page: Optional[int] = None,
    inflate: bool = True,
) -> dict:
    """
    Get a call.

    :param session: A session to use for making requests.
    :type session: aiohttp.ClientSession
    :param path: An endpoint for fetching call and related data.
    :type path: str
    :param params: API query params, defaults to None
    :type params: Optional[dict], optional
    :param page: The page number (pagination) from which we want calls, defaults to None
    :type page: Optional[int], optional
    :param inflate: If True we add call turns within the call, defaults to True
    :type inflate: bool, optional
    :return: A call response.
    :rtype: dict
    """
    if params and isinstance(page, int) and page > 0:
        params[const.PAGE] = page

    async with session.get(path, params=params) as response:
        response.raise_for_status()
        calls_response = await response.json()
        if not inflate:
            return calls_response
        calls_response[const.ITEMS] = await inflate_call(session, calls_response)
        return calls_response


async def get_metadata(url: str, token: str, params: dict) -> dict:
    """
    Get metadata for a call.

    :param url: The endpoint for fetching call and related data.
    :type url: str
    :param token: An auth token.
    :type token: str
    :param params: API query params.
    :type params: dict
    :return: A call's metadata.
    :rtype: dict
    """
    params_ = copy.deepcopy(params)
    async with aiohttp.ClientSession(
        url, headers={**get_auth_header(token)}
    ) as session:
        return await get(session, const.ROUTE__CALL, params_, inflate=False)


async def inflate_calls_in_memory(
    url: str, token: str, params: dict, pages_to_read: Iterable[int]
) -> List[dict]:
    """
    Inflate calls in memory.

    NOTE: Around 5k data points cost 41kB of memory.

    :param url: The endpoint for fetching call and related data.
    :type url: str
    :param token: An auth token.
    :type token: str
    :param params: API query params.
    :type params: dict
    :param pages_to_read: A list of pages to read calls from (paginated API).
    :type pages_to_read: Iterable[int]
    :return: A list of calls.
    :rtype: List[dict]
    """
    async with aiohttp.ClientSession(
        url, headers={**get_auth_header(token)}
    ) as session:
        responses = await asyncio.gather(
            *[
                asyncio.ensure_future(
                    get(session, const.ROUTE__CALL, params, page=page, inflate=True)
                )
                for page in pages_to_read
            ]
        )
        return [turn for response in responses for turn in response.get(const.ITEMS)]


def save_call(
    dir: str, turns: Iterable[dict], breadcrumbs: Optional[Iterable[str]] = None
) -> str:
    """
    Save a call in csv files.

    :param dir: A directory to save the call.
    :type dir: str
    :param turns: A list of call turns.
    :type turns: Iterable[dict]
    :return: Path to the saved call.
    :rtype: str
    """
    if not breadcrumbs:
        _, file_path = tempfile.mkstemp(dir=dir, suffix=".csv")
    else:
        _, file_path = tempfile.mkstemp(
            dir=dir, prefix="-".join(map(str, breadcrumbs)), suffix=".csv"
        )

    for turn in turns:
        for key, value in turn.items():
            if isinstance(value, list) or isinstance(value, dict):
                turn[key] = json.dumps(value, ensure_ascii=False)
    df = pd.DataFrame(turns)
    df.to_csv(file_path, index=False)
    return file_path


async def inflate_calls_in_files(
    url: str, token: str, params: dict, pages_to_read: Iterable[int]
) -> str:
    temp_dir = tempfile.mkdtemp()
    async with aiohttp.ClientSession(
        url, headers={**get_auth_header(token)}
    ) as session:
        for page in pages_to_read:
            turns = await get(
                session, const.ROUTE__CALL, params, page=page, inflate=True
            )
            save_call(temp_dir, turns, breadcrumbs=params.values())
    return temp_dir


async def sample(
    url: str,
    token: str,
    start_date: str,
    end_date: str,
    lang_code: str,
    call_quantity: int = 200,
    call_type: str = const.LIVE,
    ignore_callers: Optional[List[str]] = None,
    reported: bool = True,
    resolved: bool = True,
    custom_search_key: Optional[str] = None,
    custom_search_value: Optional[str] = None,
    save: Optional[str] = None,
) -> str:
    """
    Sample calls.

    :param url: The endpoint for fetching call and related data.
    :type url: str
    :param token: An auth token.
    :type token: str
    :param start_date: A start date for the sampling.
    :type start_date: str
    :param end_date: An end date for the sampling.
    :type end_date: str
    :param lang_code: A language code.
    :type lang_code: str
    :param call_quantity: Number of calls to be fetched, defaults to 200
    :type call_quantity: int, optional
    :param call_type: Pick the environment (live or subtesting), defaults to const.LIVE
    :type call_type: str, optional
    :param ignore_callers: A list of callers that should be ignored from sampling, defaults to None
    :type ignore_callers: Optional[List[str]], optional
    :param reported: If True filter only reported calls, defaults to True
    :type reported: bool, optional
    :param resolved: If True filter only resolved calls, defaults to True
    :type resolved: bool, optional
    :param custom_search_key: Custom search filter key, defaults to None
    :type custom_search_key: Optional[str], optional
    :param custom_search_value: Value for custom search filter key, defaults to None
    :type custom_search_value: Optional[str], optional
    :param inflate: To "in-memory" (works for <5k calls) vs "files", defaults to None
    :type save: Optional[str], optional
    :return: A directory path if save is set to "files" otherwise path to a file.
    :rtype: str
    """
    params = {
        const.START_DATE: start_date,
        const.END_DATE: end_date,
        const.LANG_CODE: lang_code,
        const.PAGE_SIZE: 1,
        const.CALL_TYPE: call_type,
        const.IGNORED_CALLER_NUMBERS: ignore_callers
        or const.DEFAULT_IGNORE_CALLERS_LIST,
        const.TAB: build_call_tag_filter(reported, resolved),
    }

    if custom_search_key and custom_search_value:
        params[const.CUSTOM_SEARCH_KEY] = custom_search_key
        params[const.CUSTOM_SEARCH_VALUE] = custom_search_value

    logger.debug(f"Sampling calls using:\n {params=}")

    metadata = await get_metadata(url, token, params)

    logger.debug(f"metadata={metadata}")

    if metadata.get(const.TOTAL_ITEMS) == 0:
        raise ValueError(f"No calls found for {params}")

    current_page = metadata.get(const.PAGE, 1)
    total_pages = metadata.get(const.TOTAL_PAGES, 2)

    pages_to_read = get_pages_to_read(current_page, total_pages, call_quantity)

    logger.debug(f"{pages_to_read=}")

    if isinstance(save, str) and save:
        inflate_option = save
    else:
        inflate_option = (
            const.FILES if call_quantity >= const.MEMORY_LIMIT else const.IN_MEMORY
        )

    if inflate_option == const.FILES:
        return await inflate_calls_in_files(url, token, params, pages_to_read)
    else:
        calls = await inflate_calls_in_memory(url, token, params, pages_to_read)
        return save_call(tempfile.mkdtemp(), calls, breadcrumbs=params.values())
