"""Tests for the synse.models package."""

import datetime

from synse import models


def test_make_response_nonetype() -> None:
    response = ['a', 'b', 'c']

    resp = models.make_response(None, response)

    assert resp == response


def test_response_list_data() -> None:
    response = [
        {
            'timestamp': '2019-04-22T13:30:00Z',
            'status': 'ok',
        },
        {
            'timestamp': '2019-04-22T13:40:00Z',
            'status': 'ok',
        },
    ]

    resp = models.make_response(models.Status, response)

    assert isinstance(resp, list)
    assert len(resp) == 2

    assert isinstance(resp[0], models.Status)
    assert resp[0].status == 'ok'
    assert resp[0].timestamp == datetime.datetime(2019, 4, 22, 13, 30, tzinfo=datetime.timezone.utc)
    assert resp[0]._data == response[0]

    assert isinstance(resp[0], models.Status)
    assert resp[1].status == 'ok'
    assert resp[1].timestamp == datetime.datetime(2019, 4, 22, 13, 40, tzinfo=datetime.timezone.utc)
    assert resp[1]._data == response[1]


def test_response_config() -> None:
    response = {
        'a': 1,
        'b': True,
        'c': {
            'd': {
                'e': 'foo',
            },
        },
    }

    resp = models.make_response(models.Config, response)

    assert isinstance(resp, models.Config)
    assert resp._data == response


def test_response_device_info() -> None:
    response = {
        'unknown_field': 'foo',
        'id': '123',
        'metadata': {'vapor': 'io'},
        'plugin': '456',
        'timestamp': '2019-04-22T13:30:00Z',
        'type': 'test',
    }

    resp = models.make_response(models.DeviceInfo, response)

    assert isinstance(resp, models.DeviceInfo)
    assert resp.capabilities is None
    assert resp.id == '123'
    assert resp.info is None
    assert resp.metadata == {'vapor': 'io'}
    assert resp.outputs is None
    assert resp.plugin == '456'
    assert resp.tags is None
    assert resp.timestamp == datetime.datetime(2019, 4, 22, 13, 30, tzinfo=datetime.timezone.utc)
    assert resp.type == 'test'

    assert resp._data == response


def test_response_device_summary() -> None:
    response = {
        'unknown_field': 'foo',
        'id': '123',
        'alias': 'vaporio',
        'plugin': '456',
        'type': 'test',
        'metadata': {'foo': 'bar'}
    }

    resp = models.make_response(models.DeviceSummary, response)

    assert isinstance(resp, models.DeviceSummary)
    assert resp.alias == 'vaporio'
    assert resp.id == '123'
    assert resp.info is None
    assert resp.plugin == '456'
    assert resp.tags is None
    assert resp.type == 'test'
    assert resp.metadata == {'foo': 'bar'}

    assert resp._data == response


def test_response_plugin_health() -> None:
    response = {
        'unknown_field': 'foo',
        'active': 1,
        'healthy': ['123'],
        'unhealthy': ['456'],
        'status': 'OK',
        'updated': '2019-04-22T13:30:00Z',
    }

    resp = models.make_response(models.PluginHealth, response)

    assert isinstance(resp, models.PluginHealth)
    assert resp.active == 1
    assert resp.healthy == ['123']
    assert resp.unhealthy == ['456']
    assert resp.inactive is None
    assert resp.status == 'OK'
    assert resp.updated == datetime.datetime(2019, 4, 22, 13, 30, tzinfo=datetime.timezone.utc)

    assert resp._data == response


def test_response_plugin_info() -> None:
    response = {
        'unknown_field': 'foo',
        'active': True,
        'description': 'foobar',
        'id': '456',
        'network': {
            'protocol': 'tcp',
        },
    }

    resp = models.make_response(models.PluginInfo, response)

    assert isinstance(resp, models.PluginInfo)
    assert resp.active is True
    assert resp.description == 'foobar'
    assert resp.health is None
    assert resp.id == '456'
    assert resp.maintainer is None
    assert resp.name is None
    assert resp.network == {'protocol': 'tcp'}
    assert resp.tag is None
    assert resp.version is None
    assert resp.vcs is None

    assert resp._data == response


def test_response_plugin_summary() -> None:
    response = {
        'unknown_field': 'foo',
        'active': True,
        'description': 'foobar',
        'id': '456',
        'network': {
            'protocol': 'tcp',
        },
    }

    resp = models.make_response(models.PluginSummary, response)

    assert isinstance(resp, models.PluginSummary)
    assert resp.active is True
    assert resp.description == 'foobar'
    assert resp.id == '456'
    assert resp.maintainer is None
    assert resp.name is None

    assert resp._data == response


def test_response_reading() -> None:
    response = {
        'unknown_field': 'foo',
        'context': {},
        'device': '123',
        'timestamp': '2019-04-22T13:30:00Z',
        'value': 12.4
    }

    resp = models.make_response(models.Reading, response)

    assert isinstance(resp, models.Reading)
    assert resp.context == {}
    assert resp.device == '123'
    assert resp.device_type is None
    assert resp.timestamp == datetime.datetime(2019, 4, 22, 13, 30, tzinfo=datetime.timezone.utc)
    assert resp.type is None
    assert resp.unit is None
    assert resp.value == 12.4

    assert resp._data == response


def test_response_status() -> None:
    response = {
        'unknown_field': 'foo',
        'timestamp': '2019-04-22T13:30:00Z',
        'status': 'ok',
    }

    resp = models.make_response(models.Status, response)

    assert isinstance(resp, models.Status)
    assert resp.status == 'ok'
    assert resp.timestamp == datetime.datetime(2019, 4, 22, 13, 30, tzinfo=datetime.timezone.utc)

    assert resp._data == response


def test_response_transaction_info() -> None:
    response = {
        'unknown_field': 'foo',
        'context': {},
        'device': '123',
        'timeout': '5s',
        'id': '789',
    }

    resp = models.make_response(models.TransactionInfo, response)

    assert isinstance(resp, models.TransactionInfo)
    assert resp.context == {}
    assert resp.device == '123'
    assert resp.timeout == '5s'
    assert resp.id == '789'

    assert resp._data == response


def test_response_transaction_status() -> None:
    response = {
        'unknown_field': 'foo',
        'context': {},
        'created': '2019-04-22T13:30:00Z',
        'updated': '2019-04-22T13:30:00Z',
        'id': '789',
        'timeout': '5s',
        'status': 'DONE',
    }

    resp = models.make_response(models.TransactionStatus, response)

    assert isinstance(resp, models.TransactionStatus)
    assert resp.context == {}
    assert resp.created == datetime.datetime(2019, 4, 22, 13, 30, tzinfo=datetime.timezone.utc)
    assert resp.device is None
    assert resp.id == '789'
    assert resp.message is None
    assert resp.status == 'DONE'
    assert resp.timeout == '5s'
    assert resp.updated == datetime.datetime(2019, 4, 22, 13, 30, tzinfo=datetime.timezone.utc)

    assert resp._data == response


def test_response_version() -> None:
    response = {
        'unknown_field': 'foo',
        'version': '3.0.0',
        'api_version': 'v3',
    }

    resp = models.make_response(models.Version, response)

    assert isinstance(resp, models.Version)
    assert resp.api_version == 'v3'
    assert resp.version == '3.0.0'

    assert resp._data == response
