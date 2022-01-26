import pytest
import asyncio
from concurrent.futures import Future
from rx import operators as rxop

from zaber_motion.call import call, call_sync, call_async
from zaber_motion.events import events
from zaber_motion.protobufs import main_pb2
from zaber_motion import RequestTimeoutException, InvalidPacketException


def test_request_response():
    request = main_pb2.TestRequest()
    request.data_ping = "Hello"

    response = main_pb2.TestResponse()
    call("test/request", request, response)

    assert response.data_pong == 'Hello...'

@pytest.mark.asyncio
async def test_request_response_async():
    request = main_pb2.TestRequest()
    request.data_ping = "Hello"

    response = main_pb2.TestResponse()
    await call_async("test/request", request, response)

    assert response.data_pong == 'Hello...'

@pytest.mark.asyncio
async def test_request_response_async_cancel():
    """
    Tests that cancellation does not cause an issue for async call
    """
    async def task_func():
        request = main_pb2.TestRequest()
        request.data_ping = "Hello"

        response = main_pb2.TestResponse()

        asyncio.current_task().cancel()
        await call_async("test/request", request, response)

    try:
        task = asyncio.create_task(task_func())
    except AttributeError:
        pytest.skip('Unsupported Python version')

    try:
        await task
    except asyncio.CancelledError:
        pass

def test_request_response_sync():
    request = main_pb2.TestRequest()
    request.data_ping = "Hello"

    response = main_pb2.TestResponse()
    call_sync("test/request", request, response)

    assert response.data_pong == 'Hello...'

def test_request_error():
    request = main_pb2.TestRequest()
    request.data_ping = "Hello"
    request.return_error = True

    try:
        response = main_pb2.TestResponse()
        call("test/request", request, response)
        assert False, "No error thrown"
    except RequestTimeoutException as e:
        assert e.message == "Device has not responded in given timeout"
        assert str(e) == "RequestTimeoutException: Device has not responded in given timeout"

def test_request_error_with_data():
    request = main_pb2.TestRequest()
    request.return_error_with_data = True

    try:
        response = main_pb2.TestResponse()
        call("test/request", request, response)
        assert False, "No error thrown"
    except InvalidPacketException as e:
        expected_packet = '123'
        expected_reason = 'For test'
        expected_message = 'Cannot parse incoming packet: "{}" ({})'.format(expected_packet, expected_reason)
        assert e.message == expected_message
        assert str(e) == 'InvalidPacketException: ' + expected_message
        assert e.details.packet == expected_packet
        assert e.details.reason == expected_reason

def test_request_no_response():
    response = call("test/request_no_response")
    assert response == None


def test_request_long_response():
    request = main_pb2.TestRequest()
    request.data_ping = "Hello"

    response = main_pb2.TestResponseLong()
    call("test/request_long", request, response)

    for i in range(len(response.data_pong)):
        assert response.data_pong[i] == 'Hello...{}'.format(i)


def test_event():
    promise = Future()
    with events.pipe(rxop.take(1)).subscribe(lambda event: promise.set_result(event)):
        call("test/emit_event")

        event = promise.result()
        assert event[0] == "test/event"
        assert event[1].data == "testing event data"
