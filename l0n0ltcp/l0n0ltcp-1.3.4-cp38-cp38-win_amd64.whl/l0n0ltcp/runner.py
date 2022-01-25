from l0n0lutils.async_runner import g_async_runner
import asyncio

clients = {}
servers = {}
closed = False


def regist_client(c):
    if closed:
        return False
    clients[c] = True
    return True


def regist_server(s):
    if closed:
        return False
    servers[s] = True
    return True


def unregist_client(c):
    if clients.get(c):
        del clients[c]


def unregist_server(s):
    if servers.get(s):
        del servers[s]


def is_process_closed():
    return closed


def on_process_close():
    global closed
    closed = True

    for c in clients.keys():
        c.close(False)
    clients.clear()

    for s in servers.keys():
        s.close(False)
    servers.clear()


def run_forever(loop: asyncio.BaseEventLoop = asyncio.get_event_loop()):
    g_async_runner.on_close_function(on_process_close)
    g_async_runner.run(loop)
