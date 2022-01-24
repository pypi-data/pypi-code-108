from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.disambiguate_form import DisambiguateForm
from ...models.query_result_file import QueryResultFile
from ...models.query_result_term_vector import QueryResultTermVector
from ...models.query_result_text import QueryResultText
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    multipart_data: DisambiguateForm,
) -> Dict[str, Any]:
    url = "{}/disambiguate".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    multipart_multipart_data = multipart_data.to_multipart()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "files": multipart_multipart_data,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[Any, Union[QueryResultFile, QueryResultTermVector, QueryResultText]]]:
    if response.status_code == 200:

        def _parse_response_200(data: object) -> Union[QueryResultFile, QueryResultTermVector, QueryResultText]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200_type_0 = QueryResultText.from_dict(data)

                return response_200_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200_type_1 = QueryResultTermVector.from_dict(data)

                return response_200_type_1
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            response_200_type_2 = QueryResultFile.from_dict(data)

            return response_200_type_2

        response_200 = _parse_response_200(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = response.json()

        return response_404
    if response.status_code == 400:
        response_400 = response.json()

        return response_400
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[Any, Union[QueryResultFile, QueryResultTermVector, QueryResultText]]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    multipart_data: DisambiguateForm,
) -> Response[Union[Any, Union[QueryResultFile, QueryResultTermVector, QueryResultText]]]:
    kwargs = _get_kwargs(
        client=client,
        multipart_data=multipart_data,
    )

    response = httpx.post(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    multipart_data: DisambiguateForm,
) -> Optional[Union[Any, Union[QueryResultFile, QueryResultTermVector, QueryResultText]]]:
    """ """

    return sync_detailed(
        client=client,
        multipart_data=multipart_data,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    multipart_data: DisambiguateForm,
) -> Response[Union[Any, Union[QueryResultFile, QueryResultTermVector, QueryResultText]]]:
    kwargs = _get_kwargs(
        client=client,
        multipart_data=multipart_data,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    multipart_data: DisambiguateForm,
) -> Optional[Union[Any, Union[QueryResultFile, QueryResultTermVector, QueryResultText]]]:
    """ """

    return (
        await asyncio_detailed(
            client=client,
            multipart_data=multipart_data,
        )
    ).parsed
