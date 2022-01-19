"""
    lager.gateway.tunnel

    GDB tunnel functions
"""
import functools
import logging
import click
import trio
import lager_trio_websocket as trio_websocket
from ..util import heartbeat

logger = logging.getLogger(__name__)

async def send_to_websocket(websocket, gdb_client_stream, nursery):
    """
        Read data from gdb_client_stream (a trio stream connected to a gdb client)
        and send to websocket (ultimate destination is gateway gdbserver).
    """
    try:
        async with gdb_client_stream:
            async for msg in gdb_client_stream:
                await websocket.send_message(msg)
    except trio.BrokenResourceError:
        pass
    finally:
        nursery.cancel_scope.cancel()


async def send_to_gdb(websocket, gdb_client_stream, nursery):
    """
        Read data from websocket (originating from gateway gdbserver)
        and send to gdb_client_stream (a trio stream connected to a gdb client)
    """
    while True:
        try:
            msg = await websocket.get_message()
            await gdb_client_stream.send_all(msg)
        except trio_websocket.ConnectionClosed:
            nursery.cancel_scope.cancel()

async def cloud_connection_handler(connection_params, gdb_client_stream, debug=True):
    """
        Handle a single connection from a gdb client
    """
    (uri, kwargs) = connection_params
    sockname = gdb_client_stream.socket.getsockname()
    if debug:
        click.echo(f'Serving client: {sockname}')
    try:
        async with trio_websocket.open_websocket_url(uri, disconnect_timeout=1, **kwargs) as websocket:
            async with trio.open_nursery() as nursery:
                nursery.start_soon(send_to_websocket, websocket, gdb_client_stream, nursery)
                nursery.start_soon(send_to_gdb, websocket, gdb_client_stream, nursery)
                nursery.start_soon(heartbeat, websocket, 30, 30)
    except trio_websocket.ConnectionRejected as exc:
        click.secho('Connection to Lager Gateway rejected. Is the Gateway '\
                    'powered on and have a solid internet connection?', fg='red', err=True)
        if debug:
            logger.exception('Exception in connection_handler', exc_info=exc)
    except trio.ClosedResourceError:
        click.secho('Tunnel connection closed', fg='yellow', err=True)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception('Exception in connection_handler', exc_info=exc)
    finally:
        if debug:
            click.echo(f'client disconnected: {sockname}')

async def send_to_local_client(gateway_stream, gdb_client_stream, nursery):
    try:
        async for data in gateway_stream:
            await gdb_client_stream.send_all(data)
        try:
            await gdb_client_stream.send_eof()
        except trio.BrokenResourceError:
            pass
    except Exception as exc:
        logger.exception('send_to_local_client failed: ', exc_info=exc)
        nursery.cancel_scope.cancel()

async def send_to_local_gateway(gateway_stream, gdb_client_stream, nursery):
    try:
        async for data in gdb_client_stream:
            await gateway_stream.send_all(data)
        try:
            await gateway_stream.send_eof()
        except trio.BrokenResourceError:
            pass
    except Exception as exc:
        logger.exception('send_to_local_gateway failed: ', exc_info=exc)
        nursery.cancel_scope.cancel()

async def local_connection_handler(session, gateway, remote_host, remote_port, gdb_client_stream, debug=True):
    """
        Handle a single connection from a gdb client
    """
    sockname = gdb_client_stream.socket.getsockname()
    if not remote_host:
        resp = await trio.to_thread.run_sync(session.start_local_gdb_tunnel, gateway, False)
        resp = resp.json()
        # resp = session.start_local_gdb_tunnel(gateway, False).json()
        remote_host = resp['host']
        remote_port = int(resp['port'])
    if debug:
        click.echo(f'Serving client: {sockname}')
    try:
        async with await trio.open_tcp_stream(remote_host, remote_port) as gateway_stream:
            async with trio.open_nursery() as nursery:
                nursery.start_soon(send_to_local_client, gateway_stream, gdb_client_stream, nursery)
                nursery.start_soon(send_to_local_gateway, gateway_stream, gdb_client_stream, nursery)
    except OSError:
        click.secho('Failed to connect to gateway. Are you sure you\'re on the same network as your gateway?', fg='red', err=True)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception('Exception in connection_handler', exc_info=exc)
    finally:
        click.echo(f'client disconnected: {sockname}')

async def serve_tunnel(host, port, connection_params, name, debug=True, rtt=None, *, task_status=trio.TASK_STATUS_IGNORED):
    """
        Start up the server that tunnels traffic to a gdbserver instance running on a gateway
    """
    async with trio.open_nursery() as nursery:
        # print(rtt)
        handler = functools.partial(cloud_connection_handler, connection_params, debug=debug)
        serve_listeners = functools.partial(trio.serve_tcp, handler, port, host=host)

        if rtt:
            print(rtt)
            rtt_handler = functools.partial(cloud_connection_handler, rtt, debug=debug)
            rtt_serve_listeners = functools.partial(trio.serve_tcp, rtt_handler, 9090, host=host)
            await nursery.start(rtt_serve_listeners)
            click.echo(f'Serving RTT on {host}:9090')

        server = await nursery.start(serve_listeners)
        task_status.started(server)

        if name and debug:
            click.echo(f'Serving {name} on {host}:{port}. Press Ctrl+C to quit.')
        try:
            await trio.sleep_forever()
        except KeyboardInterrupt:
            nursery.cancel_scope.cancel()

async def serve_local_tunnel(session, gateway, host, port, fork, *, task_status=trio.TASK_STATUS_IGNORED):
    """
        Start up the server that locally tunnels traffic to a gdbserver instance running on a gateway
    """
    remote_host = None
    remote_port = None
    if fork:
        resp = session.start_local_gdb_tunnel(gateway, True).json()
        remote_host = resp['host']
        remote_port = int(resp['port'])

    async with trio.open_nursery() as nursery:
        handler = functools.partial(local_connection_handler, session, gateway, remote_host, remote_port)
        serve_listeners = functools.partial(trio.serve_tcp, handler, port, host=host)

        server = await nursery.start(serve_listeners)
        task_status.started(server)
        click.echo(f'Serving GDB on {host}:{port}. Press Ctrl+C to quit.')
        try:
            await trio.sleep_forever()
        except KeyboardInterrupt:
            nursery.cancel_scope.cancel()
