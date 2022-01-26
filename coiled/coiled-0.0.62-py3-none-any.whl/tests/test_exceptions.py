import pytest
from coiled.errors import ServerError
from coiled.websockets import WebsocketConnector


@pytest.mark.asyncio
async def test_unhandled_websocket_exception(settings, cloud):
    settings.FF_SUPPRESS_UNKNOWN_EXCEPTIONS = True
    ws_server = cloud.server.replace("http", "ws", 1)
    ws_endpoint = f"{ws_server}/ws/api/v1/testing/exception/"
    session = cloud._ensure_session()
    ws = WebsocketConnector(
        endpoint=ws_endpoint,
        notifications_endpoint=f"{ws_server}/ws/api/v1/{cloud._default_account}/notifications/",
        session=session,
    )
    await ws.connect()
    await ws.send_json({"test": "test"})
    with pytest.raises(ServerError) as server_error:
        await ws.stream_messages()
    assert (
        "Coiled cloud encountered an unknown issue handling your request, contact customer service and quote ID".lower()
        in str(server_error.value).lower()
    )


@pytest.mark.asyncio
async def test_unhandled_websocket_exception_ff_off(settings, cloud):
    settings.FF_SUPPRESS_UNKNOWN_EXCEPTIONS = False
    ws_server = cloud.server.replace("http", "ws", 1)
    ws_endpoint = f"{ws_server}/ws/api/v1/testing/exception/"
    session = cloud._ensure_session()
    ws = WebsocketConnector(
        endpoint=ws_endpoint,
        notifications_endpoint=f"{ws_server}/ws/api/v1/{cloud._default_account}/notifications/",
        session=session,
    )
    await ws.connect()
    await ws.send_json({"test": "test"})
    with pytest.raises(ServerError) as server_error:
        await ws.stream_messages()
    assert (
        "cloud.consumers.testing.WebsocketExceptionTest: Test".lower()
        in str(server_error.value).lower()
    )


@pytest.mark.asyncio
async def test_api_websocket_exception(settings, cloud):
    session = cloud._ensure_session()
    ws_server = cloud.server.replace("http", "ws", 1)
    ws_endpoint = f"{ws_server}/ws/api/v1/testing/api-exception/"
    session = cloud._ensure_session()
    ws = WebsocketConnector(
        endpoint=ws_endpoint,
        notifications_endpoint=f"{ws_server}/ws/api/v1/{cloud._default_account}/notifications/",
        session=session,
    )
    await ws.connect()
    await ws.send_json({"test": "test"})
    with pytest.raises(ServerError) as server_error:
        await ws.stream_messages()
    assert "this message should be shown to user" == str(server_error.value)
