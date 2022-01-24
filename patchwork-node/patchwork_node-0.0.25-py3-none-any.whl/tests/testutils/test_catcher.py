# -*- coding: utf-8 -*-
from google.protobuf.wrappers_pb2 import BytesValue, StringValue
from patchwork.core import Task

from patchwork.node.testutils.worker import TaskCatcher


def test_catcher_assert_task_type_match():
    tc = TaskCatcher()
    task = Task(task_type='test')

    delta = tc.compare_tasks(task, {
        'task_type': 'test'
    })

    assert not delta


def test_catcher_assert_task_type_not_match():
    tc = TaskCatcher()
    task = Task(task_type='test')

    delta = tc.compare_tasks(task, {
        'task_type': 'another-test'
    })

    assert delta == {'task_type'}


def test_catcher_assert_task_uuid_match():
    tc = TaskCatcher()
    task = Task(uuid='unique-identifier')

    delta = tc.compare_tasks(task, {
        'uuid': 'unique-identifier'
    })

    assert not delta


def test_catcher_assert_task_uuid_not_match():
    tc = TaskCatcher()
    task = Task(uuid='unique-identifier')

    delta = tc.compare_tasks(task, {
        'uuid': 'another-identifier'
    })

    assert delta == {'uuid'}


def test_catcher_assert_task_correlation_id_match():
    tc = TaskCatcher()
    task = Task(correlation_id='correlation')

    delta = tc.compare_tasks(task, {
        'correlation_id': 'correlation'
    })

    assert not delta


def test_catcher_assert_task_correlation_id_not_match():
    tc = TaskCatcher()
    task = Task(correlation_id='correlation')

    delta = tc.compare_tasks(task, {
        'correlation_id': 'uncorrelated'
    })

    assert delta == {'correlation_id'}


def test_catcher_assert_task_payload_bytes_match():
    tc = TaskCatcher()
    task = Task()
    payload = BytesValue(value=b'data')
    task.payload.Pack(payload)

    delta = tc.compare_tasks(task, {
        'payload': b'data'
    })

    assert not delta


def test_catcher_assert_task_payload_bytes_not_match():
    tc = TaskCatcher()
    task = Task()
    payload = BytesValue(value=b'data')
    task.payload.Pack(payload)

    delta = tc.compare_tasks(task, {
        'payload': b'invalid-data'
    })

    assert delta == {'payload'}


def test_catcher_assert_task_payload_string_match():
    tc = TaskCatcher()
    task = Task()
    payload = StringValue(value='data')
    task.payload.Pack(payload)

    delta = tc.compare_tasks(task, {
        'payload': 'data'
    })

    assert not delta


def test_catcher_assert_task_payload_string_not_match():
    tc = TaskCatcher()
    task = Task()
    payload = StringValue(value='data')
    task.payload.Pack(payload)

    delta = tc.compare_tasks(task, {
        'payload': 'invalid-data'
    })

    assert delta == {'payload'}


def test_catcher_assert_task_payload_type_not_match():
    tc = TaskCatcher()
    task = Task()
    payload = BytesValue(value=b'expected-bytes-data')
    task.payload.Pack(payload)

    delta = tc.compare_tasks(task, {
        'payload': 'invalid-type-its-string'
    })

    assert delta == {'payload.@type'}


def test_catcher_assert_task_payload_protobuf_match():
    tc = TaskCatcher()
    task = Task()
    payload = StringValue(value='data')
    task.payload.Pack(payload)

    delta = tc.compare_tasks(task, {
        'payload': StringValue(value='data')
    })

    assert not delta


def test_catcher_assert_task_payload_protobuf_not_match():
    tc = TaskCatcher()
    task = Task()
    payload = StringValue(value='data')
    task.payload.Pack(payload)

    delta = tc.compare_tasks(task, {
        'payload': StringValue(value='invalid-data')
    })

    assert delta == {'payload'}
