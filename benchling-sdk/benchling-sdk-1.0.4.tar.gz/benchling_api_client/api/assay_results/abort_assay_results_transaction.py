from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.assay_result_transaction_create_response import AssayResultTransactionCreateResponse
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    transaction_id: str,
) -> Dict[str, Any]:
    url = "{}/result-transactions/{transaction_id}:abort".format(
        client.base_url, transaction_id=transaction_id
    )

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[AssayResultTransactionCreateResponse]:
    if response.status_code == 200:
        response_200 = AssayResultTransactionCreateResponse.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[AssayResultTransactionCreateResponse]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    transaction_id: str,
) -> Response[AssayResultTransactionCreateResponse]:
    kwargs = _get_kwargs(
        client=client,
        transaction_id=transaction_id,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    transaction_id: str,
) -> Optional[AssayResultTransactionCreateResponse]:
    """ Aborting a transaction will discard all uploaded results. """

    return sync_detailed(
        client=client,
        transaction_id=transaction_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    transaction_id: str,
) -> Response[AssayResultTransactionCreateResponse]:
    kwargs = _get_kwargs(
        client=client,
        transaction_id=transaction_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    transaction_id: str,
) -> Optional[AssayResultTransactionCreateResponse]:
    """ Aborting a transaction will discard all uploaded results. """

    return (
        await asyncio_detailed(
            client=client,
            transaction_id=transaction_id,
        )
    ).parsed
