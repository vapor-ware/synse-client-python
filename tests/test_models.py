
import datetime

from synse import models


class FakeResponse:
    """Class to fake a requests.Response.

    All we need for the models tests is the ``json`` method.
    """

    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data


def test_response_config():
    fake_response = FakeResponse({
        'a': 1,
        'b': True,
        'c': {
            'd': {
                'e': 'foo',
            },
        },
    })

    resp = models.Config(fake_response)

    assert resp.response == fake_response
    assert resp.raw == fake_response.data


def test_response_device_info():
    fake_response = FakeResponse({
        'unknown_field': 'foo',
        'id': '123',
        'metadata': {'vapor': 'io'},
        'plugin': '456',
        'timestamp': '2019-04-22T13:30:00Z',
        'type': 'test',
    })

    resp = models.DeviceInfo(fake_response)

    assert resp.capabilities is None
    assert resp.id == '123'
    assert resp.info is None
    assert resp.metadata == {'vapor': 'io'}
    assert resp.output is None
    assert resp.plugin == '456'
    assert resp.tags is None
    assert resp.timestamp == datetime.datetime(2019, 4, 22, 13, 30, tzinfo=datetime.timezone.utc)
    assert resp.type == 'test'

    assert resp.response == fake_response
    assert resp.raw == fake_response.data


def test_response_device_summary():
    fake_response = FakeResponse({
        'unknown_field': 'foo',
        'id': '123',
        'alias': 'vaporio',
        'plugin': '456',
        'type': 'test',
    })

    resp = models.DeviceSummary(fake_response)

    assert resp.alias == 'vaporio'
    assert resp.id == '123'
    assert resp.info is None
    assert resp.plugin == '456'
    assert resp.tags is None
    assert resp.type == 'test'

    assert resp.response == fake_response
    assert resp.raw == fake_response.data


def test_response_plugin_health():
    fake_response = FakeResponse({
        'unknown_field': 'foo',
        'active': 1,
        'healthy': ['123'],
        'unhealthy': ['456'],
        'status': 'OK',
        'updated': '2019-04-22T13:30:00Z',
    })

    resp = models.PluginHealth(fake_response)

    assert resp.active == 1
    assert resp.healthy == ['123']
    assert resp.unhealthy == ['456']
    assert resp.inactive is None
    assert resp.status == 'OK'
    assert resp.updated == datetime.datetime(2019, 4, 22, 13, 30, tzinfo=datetime.timezone.utc)

    assert resp.response == fake_response
    assert resp.raw == fake_response.data


def test_response_plugin_info():
    fake_response = FakeResponse({
        'unknown_field': 'foo',
        'active': True,
        'description': 'foobar',
        'id': '456',
        'network': {
            'protocol': 'tcp',
        },
    })

    resp = models.PluginInfo(fake_response)

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

    assert resp.response == fake_response
    assert resp.raw == fake_response.data


def test_response_plugin_summary():
    fake_response = FakeResponse({
        'unknown_field': 'foo',
        'active': True,
        'description': 'foobar',
        'id': '456',
        'network': {
            'protocol': 'tcp',
        },
    })

    resp = models.PluginSummary(fake_response)

    assert resp.active is True
    assert resp.description == 'foobar'
    assert resp.id == '456'
    assert resp.maintainer is None
    assert resp.name is None

    assert resp.response == fake_response
    assert resp.raw == fake_response.data


def test_response_reading():
    fake_response = FakeResponse({
        'unknown_field': 'foo',
        'context': {},
        'device': '123',
        'timestamp': '2019-04-22T13:30:00Z',
        'value': 12.4
    })

    resp = models.Reading(fake_response)

    assert resp.context == {}
    assert resp.device == '123'
    assert resp.device_type is None
    assert resp.timestamp == datetime.datetime(2019, 4, 22, 13, 30, tzinfo=datetime.timezone.utc)
    assert resp.type is None
    assert resp.unit is None
    assert resp.value == 12.4

    assert resp.response == fake_response
    assert resp.raw == fake_response.data


def test_response_status():
    fake_response = FakeResponse({
        'unknown_field': 'foo',
        'timestamp': '2019-04-22T13:30:00Z',
        'status': 'ok',
    })

    resp = models.Status(fake_response)

    assert resp.status == 'ok'
    assert resp.timestamp == datetime.datetime(2019, 4, 22, 13, 30, tzinfo=datetime.timezone.utc)

    assert resp.response == fake_response
    assert resp.raw == fake_response.data


def test_response_transaction_info():
    fake_response = FakeResponse({
        'unknown_field': 'foo',
        'context': {},
        'device': '123',
        'timeout': '5s',
        'transaction': '789',
    })

    resp = models.TransactionInfo(fake_response)

    assert resp.context == {}
    assert resp.device == '123'
    assert resp.timeout == '5s'
    assert resp.transaction == '789'

    assert resp.response == fake_response
    assert resp.raw == fake_response.data


def test_response_transaction_status():
    fake_response = FakeResponse({
        'unknown_field': 'foo',
        'context': {},
        'created': '2019-04-22T13:30:00Z',
        'updated': '2019-04-22T13:30:00Z',
        'id': '789',
        'timeout': '5s',
        'status': 'DONE',
    })

    resp = models.TransactionStatus(fake_response)

    assert resp.context == {}
    assert resp.created == datetime.datetime(2019, 4, 22, 13, 30, tzinfo=datetime.timezone.utc)
    assert resp.device is None
    assert resp.id == '789'
    assert resp.message is None
    assert resp.status == 'DONE'
    assert resp.timeout == '5s'
    assert resp.updated == datetime.datetime(2019, 4, 22, 13, 30, tzinfo=datetime.timezone.utc)

    assert resp.response == fake_response
    assert resp.raw == fake_response.data


def test_response_version():
    fake_response = FakeResponse({
        'unknown_field': 'foo',
        'version': '3.0.0',
        'api_version': 'v3',
    })

    resp = models.Version(fake_response)

    assert resp.api_version == 'v3'
    assert resp.version == '3.0.0'

    assert resp.response == fake_response
    assert resp.raw == fake_response.data
