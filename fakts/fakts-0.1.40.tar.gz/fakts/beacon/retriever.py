from abc import abstractmethod
from typing import Generic, Type, TypeVar
from pydantic.main import BaseModel
from fakts.beacon.beacon import FaktsEndpoint
import webbrowser
import asyncio
import uuid
from aiohttp import web
from urllib.parse import quote, urlencode, parse_qs
from koil import koil
import json
import logging

logger = logging.getLogger(__name__)


class RetrieverException(Exception):
    pass


class IncorrectStateException(Exception):
    pass


def wrapped_get_future(future: asyncio.Future, state: str):
    async def web_token_response(request):
        loop = asyncio.get_event_loop()
        logger.info("Received Reply from user")
        result = parse_qs(request.query_string)
        qs_state = result["state"][0]
        config = json.loads(result["config"][0])

        if qs_state != state:
            loop.call_soon_threadsafe(
                future.set_exception, RetrieverException("Danger! Invalid State")
            )
            return web.Response(text="Error! Invalid State.")

        loop.call_soon_threadsafe(future.set_result, config)
        return web.Response(text="You can close me now !")

    return web_token_response


async def wait_for_get(
    starturl,
    previous={},
    redirect_host="localhost",
    redirect_port=6767,
    redirect_path="/",
    timeout=400,
    print_function=False,
    handle_signals=False,
):

    state = str(uuid.uuid4())

    params = {
        "state": state,
        "redirect_uri": f"http://{redirect_host}:{redirect_port}{redirect_path}",
        "scopes": previous.get("herre", {}).get("scopes", None),
        "name": previous.get("herre", {}).get("name", None),
        "client_id": previous.get("herre", {}).get("client_id", None),
    }

    querystring = urlencode(
        {key: value for key, value in params.items() if value != None}
    )

    webbrowser.open_new(starturl + "?" + querystring)

    token_future = asyncio.get_event_loop().create_future()

    app = web.Application()

    app.router.add_get(redirect_path, wrapped_get_future(token_future, state))

    webserver_task = asyncio.get_event_loop().create_task(
        web._run_app(
            app,
            host=redirect_host,
            port=redirect_port,
            print=print_function,
            handle_signals=handle_signals,
        )
    )
    done, pending = await asyncio.wait(
        [token_future, webserver_task, asyncio.sleep(timeout)],
        return_when=asyncio.FIRST_COMPLETED,
    )

    for tf in done:
        if tf == token_future:
            post_json = tf.result()
        else:
            post_json = None

    for task in pending:
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

    if not post_json:
        raise RetrieverException("No Post Data Received")
    return post_json


class FaktsRetriever:
    REDIRECT_HOST = "localhost"
    REDIRECT_PORT = 6767
    REDIRECT_PATH = "/"

    def __init__(
        self,
        *args,
        redirect_host=None,
        redirect_port=None,
        redirect_path=None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.redirect_host = redirect_host or self.REDIRECT_HOST
        self.redirect_port = redirect_port or self.REDIRECT_PORT
        self.redirect_path = redirect_path or self.REDIRECT_PATH

    async def aretrieve(self, config: FaktsEndpoint, previous={}):
        post_data = await wait_for_get(
            config.url,
            previous=previous,
            redirect_host=self.redirect_host,
            redirect_port=self.redirect_port,
            redirect_path=self.redirect_path,
        )
        return post_data

    def retrieve(self, config, as_task=True, **kwargs):
        return koil(self.aretrieve(config, **kwargs), as_task=as_task)
