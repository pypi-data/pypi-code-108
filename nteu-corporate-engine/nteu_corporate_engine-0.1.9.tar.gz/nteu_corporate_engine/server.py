#!/usr/bin/env python3.7
import os
import sys
import yaml
import logging
import uvloop
import asyncio
import pickle
from nteu_corporate_engine.engine import Engine
from aiohttp import web
from typing import Dict


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class TranslationEngineServer:

    def __init__(self, config: str = None, serialized: bool = False):
        self._app = web.Application()
        self._app["lock"] = asyncio.Lock()

        if serialized:
            if os.environ.get("PYTHONTRANSLATIONSERVERDEBUG", None) is not None:
                dbug = True 
            else:
                dbug = False
            Engine.setup_log(dbug=dbug)
            with open("engine.pkl", "rb") as engine_bts:
                self._app["engine"] = pickle.load(engine_bts)
        else:
            with open(config, "r") as file:
                config = yaml.safe_load(file)
            self._update_config(config)
            self._app["engine"] = Engine(config)
        self._app.router.add_post("/translate", handle_translate)
        self._app.router.add_post("/train", handle_train)
        self._app.router.add_post("/isready", handle_ready)

    def start(self, port: int):
        web.run_app(self._app, port=port)

    def _update_config(self, root: Dict, prefix: str = None):
        for key in root.keys():
            name = prefix + key.upper() if prefix is not None else key.upper()
            value = root[key]
            if isinstance(value, dict):
                self._update_config(value, name + "_")
            elif os.environ.get(name) is not None:
                root[key] = os.environ.get(name)


async def handle_translate(req):
    lock = req.app["lock"]
    engine = req.app["engine"]

    try:
        req = await req.json()
        batch = req.get("srcs")
        translations = await engine.process_batch(batch, lock)
        ans = {
            "tus": []
        }
        for src, translation in zip(batch, translations):
            ans["tus"].append({"src": src, "tgt": translation})
        return web.json_response(ans, status=200)

    except Exception as e:
        logging.exception(str(e))
        response_obj = {'status': 'failed', 'reason': str(e)}
        return web.json_response(response_obj, status=500)


async def handle_train(req):
    lock = req.app["lock"]
    engine = req.app["engine"]

    try:
        req = await req.json()
        num_steps = req.get("steps", 2)
        translation_units = req.get("tus")
        batch = []
        for tu in translation_units:
            if tu["tgt"] == "":
                raise Exception(
                    "Missing target segment for Online Learning Training."
                )
            batch.append((tu["src"], tu["tgt"]))
        await engine.online_train(batch, num_steps, lock)
        return web.json_response({"rc": 0}, status=200)
    except Exception as e:
        logging.exception(str(e))
        response_obj = {'status': 'failed', 'reason': str(e)}
        return web.json_response(response_obj, status=500)


async def handle_ready(req):
    return web.json_response({"rc": 0}, status=200)


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2:
        print("Three arguments needed: ")
        print("config and port")
    else:
        try:
            server = TranslationEngineServer(args[0])
            server.start(int(args[1]))
        except Exception as e:
            logging.exception(str(e))
            raise Exception("Error") from e
