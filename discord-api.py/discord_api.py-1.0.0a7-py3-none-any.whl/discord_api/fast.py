import asyncio

def setup_uvloop():
    try:
        import uvloop
    except ImportError:
        return
    if not isinstance(asyncio.get_event_loop_policy(), uvloop.EventLoopPolicy):
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

def setup_ujson(client):
    try:
        import ujson
    except ImportError:
        import json
        client.json = json
    else:
        client.json = ujson

def setup_fast(client):
    setup_uvloop()
    setup_ujson(client)
