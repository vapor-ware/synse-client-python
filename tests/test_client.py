
import typing

import pytest
import requests

from synse import client, errors, models


class TestHTTPClientV3:
    """Tests for the HTTPClientV3 class."""

    def test_init(self):
        c = client.HTTPClientV3('localhost')

        assert c.session is not None
        assert c.host == 'localhost'
        assert c.port == 5000
        assert c.timeout == 10
        assert c.base == 'http://localhost:5000'
        assert c.url == 'http://localhost:5000/v3'

    def test_make_request_error(self, mock_response):
        # The mocked request will return a connection error (an instance of
        # RequestException) if the fetched URL doesn't hit a match.
        c = client.HTTPClientV3('localhost')

        with pytest.raises(errors.SynseError):
            c.make_request(
                method='GET',
                url='http://localhost:5000/v3/bar',
            )

    def test_config(self, mock_response, synse_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/v3/config',
            json=synse_response.config,
        )

        c = client.HTTPClientV3('localhost')

        resp = c.config()

        assert isinstance(resp, models.Config)
        assert resp.raw == synse_response.config

    def test_config_error(self, mock_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/v3/config',
            status=500,
            json={
                'context': 'simulated error',
            },
        )

        c = client.HTTPClientV3('localhost')

        with pytest.raises(errors.ServerError) as e:
            c.config()
        assert str(e.value) == 'simulated error'

    def test_info(self, mock_response, synse_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/v3/info/123',
            json=synse_response.info,
        )

        c = client.HTTPClientV3('localhost')

        resp = c.info('123')

        assert isinstance(resp, models.DeviceInfo)
        assert resp.raw == synse_response.info

    def test_info_error(self, mock_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/v3/info/123',
            status=404,
            json={
                'context': 'device not found',
            },
        )

        c = client.HTTPClientV3('localhost')

        with pytest.raises(errors.NotFound) as e:
            c.info('123')
        assert str(e.value) == 'device not found'

    def test_plugin(self, mock_response, synse_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/v3/plugin/123',
            json=synse_response.plugin,
        )

        c = client.HTTPClientV3('localhost')

        resp = c.plugin('123')

        assert isinstance(resp, models.PluginInfo)
        assert resp.raw == synse_response.plugin

    def test_plugin_error(self, mock_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/v3/plugin/123',
            status=404,
            json={
                'context': 'plugin not found',
            },
        )

        c = client.HTTPClientV3('localhost')

        with pytest.raises(errors.NotFound) as e:
            c.plugin('123')
        assert str(e.value) == 'plugin not found'

    def test_plugin_health(self, mock_response, synse_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/v3/plugin/health',
            json=synse_response.plugin_health,
        )

        c = client.HTTPClientV3('localhost')

        resp = c.plugin_health()

        assert isinstance(resp, models.PluginHealth)
        assert resp.raw == synse_response.plugin_health

    def test_plugin_health_error(self, mock_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/v3/plugin/health',
            status=500,
            json={
                'context': 'simulated error',
            },
        )

        c = client.HTTPClientV3('localhost')

        with pytest.raises(errors.ServerError) as e:
            c.plugin_health()
        assert str(e.value) == 'simulated error'

    def test_plugins(self, mock_response, synse_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/v3/plugin',
            json=synse_response.plugins,
        )

        c = client.HTTPClientV3('localhost')

        resp = c.plugins()

        assert isinstance(resp, list)
        assert all(isinstance(elem, models.PluginSummary) for elem in resp)

    def test_plugins_error(self, mock_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/v3/plugin',
            status=500,
            json={
                'context': 'simulated error',
            },
        )

        c = client.HTTPClientV3('localhost')

        with pytest.raises(errors.ServerError) as e:
            c.plugins()
        assert str(e.value) == 'simulated error'

    def test_read(self, mock_response, synse_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/v3/read',
            json=synse_response.read,
        )

        c = client.HTTPClientV3('localhost')

        resp = c.read()

        assert isinstance(resp, list)
        assert all(isinstance(elem, models.Reading) for elem in resp)

    def test_read_error(self, mock_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/v3/read',
            status=400,
            json={
                'context': 'invalid arguments',
            },
        )

        c = client.HTTPClientV3('localhost')

        with pytest.raises(errors.InvalidInput) as e:
            c.read()
        assert str(e.value) == 'invalid arguments'

    @pytest.mark.parametrize(
        'ns,tags,expected', [
            (None, None, {}),
            ('default', None, {'ns': 'default'}),
            ('foo', None, {'ns': 'foo'}),
            (None, ['vapor'], {'tags': 'vapor'}),
            ('foo', ['vapor'], {'ns': 'foo', 'tags': 'vapor'}),
            ('foo', ['vapor', 'a/b'], {'ns': 'foo', 'tags': 'vapor,a/b'}),
            ('foo', ['vapor', 'a/b', '1/2:3'], {'ns': 'foo', 'tags': 'vapor,a/b,1/2:3'}),
        ]
    )
    def test_read_params(self, mocker, ns, tags, expected):
        mock_request = mocker.patch(
            'synse.client.HTTPClientV3.make_request',
            returns=requests.Response()
        )

        c = client.HTTPClientV3('localhost')
        _ = c.read(ns=ns, tags=tags)

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            url='http://localhost:5000/v3/read',
            method='get',
            params=expected,
        )

    def test_read_cache(self, mock_response, synse_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/v3/readcache',
            body=synse_response.read_cache,
            content_type='application/json',
            stream=True,
        )

        c = client.HTTPClientV3('localhost')

        resp = c.read_cache()

        assert isinstance(resp, typing.Generator)
        assert all(isinstance(elem, models.Reading) for elem in resp)

    def test_read_cache_error(self, mock_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/v3/readcache',
            status=500,
            json={
                'context': 'simulated error',
            },
            stream=True,
        )

        c = client.HTTPClientV3('localhost')

        resp = c.read_cache()

        assert isinstance(resp, typing.Generator)

        with pytest.raises(errors.ServerError) as e:
            _ = [x for x in resp]
        assert str(e.value) == 'simulated error'

    @pytest.mark.parametrize(
        'start,end,expected', [
            (None, None, {}),
            ('timestamp-1', None, {'start': 'timestamp-1'}),
            (None, 'timestamp-1', {'end': 'timestamp-1'}),
            ('timestamp-1', 'timestamp-2', {'start': 'timestamp-1', 'end': 'timestamp-2'}),
        ]
    )
    def test_read_cache_params(self, mocker, start, end, expected):
        mock_request = mocker.patch(
            'synse.client.HTTPClientV3.make_request',
            returns=requests.Response()
        )

        c = client.HTTPClientV3('localhost')
        _ = [x for x in c.read_cache(start=start, end=end)]

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            url='http://localhost:5000/v3/readcache',
            method='get',
            stream=True,
            params=expected,
        )

    def test_read_device(self, mock_response, synse_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/v3/read/123',
            json=synse_response.read_device,
        )

        c = client.HTTPClientV3('localhost')

        resp = c.read_device('123')

        assert isinstance(resp, list)
        assert all(isinstance(elem, models.Reading) for elem in resp)

    def test_read_device_error(self, mock_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/v3/read/123',
            status=500,
            json={
                'context': 'simulated error',
            },
        )

        c = client.HTTPClientV3('localhost')

        with pytest.raises(errors.ServerError) as e:
            c.read_device('123')
        assert str(e.value) == 'simulated error'

    def test_scan(self, mock_response, synse_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/v3/scan',
            json=synse_response.scan,
        )

        c = client.HTTPClientV3('localhost')

        resp = c.scan()

        assert isinstance(resp, typing.Generator)
        assert all(isinstance(elem, models.DeviceSummary) for elem in resp)

    def test_scan_error(self, mock_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/v3/scan',
            status=500,
            json={
                'context': 'simulated error',
            },
        )

        c = client.HTTPClientV3('localhost')

        with pytest.raises(errors.ServerError) as e:
            c.scan()
        assert str(e.value) == 'simulated error'

    @pytest.mark.parametrize(
        'force,ns,sort,tags,expected', [
            (None, None, None, None, {}),
            (False, None, None, None, {'force': 'False'}),
            (True, None, None, None, {'force': 'True'}),
            ('other', None, None, None, {'force': 'other'}),
            (None, 'default', None, None, {'ns': 'default'}),
            (None, 'foo', None, None, {'ns': 'foo'}),
            (None, None, 'id,type', None, {'sort': 'id,type'}),
            (None, None, 'id', None, {'sort': 'id'}),
            (None, None, None, ['vapor'], {'tags': 'vapor'}),
            (None, None, None, ['vapor', 'foo/bar'], {'tags': 'vapor,foo/bar'}),
            (None, None, None, ['vapor', 'foo/bar', 'a/b:c'], {'tags': 'vapor,foo/bar,a/b:c'}),
            (None, None, 'id,type', ['vapor', 'foo/bar', 'a/b:c'], {'sort': 'id,type', 'tags': 'vapor,foo/bar,a/b:c'}),
            (None, 'foo', 'id,type', ['vapor', 'foo/bar', 'a/b:c'], {'ns': 'foo', 'sort': 'id,type', 'tags': 'vapor,foo/bar,a/b:c'}),
            (True, 'foo', 'id,type', ['vapor', 'foo/bar', 'a/b:c'], {'force': 'True', 'ns': 'foo', 'sort': 'id,type', 'tags': 'vapor,foo/bar,a/b:c'}),
        ]
    )
    def test_scan_params(self, mocker, force, ns, sort, tags, expected):
        mock_request = mocker.patch(
            'synse.client.HTTPClientV3.make_request',
            returns=requests.Response()
        )

        c = client.HTTPClientV3('localhost')
        _ = c.scan(force=force, ns=ns, sort=sort, tags=tags)

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            url='http://localhost:5000/v3/scan',
            method='get',
            params=expected,
        )

    def test_status(self, mock_response, synse_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/test',
            json=synse_response.status,
        )

        c = client.HTTPClientV3('localhost')

        resp = c.status()

        assert isinstance(resp, models.Status)
        assert resp.raw == synse_response.status

    def test_status_error(self, mock_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/test',
            status=500,
        )

        c = client.HTTPClientV3('localhost')

        with pytest.raises(errors.ServerError) as e:
            c.status()
        assert str(e.value) == ''  # no context means no message

    def test_tags(self, mock_response, synse_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/v3/tags',
            json=synse_response.tags,
        )

        c = client.HTTPClientV3('localhost')

        resp = c.tags()

        assert isinstance(resp, list)
        assert all(isinstance(elem, str) for elem in resp)

    def test_tags_error(self, mock_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/v3/tags',
            status=500,
            json={
                'context': 'simulated error',
            },
        )

        c = client.HTTPClientV3('localhost')

        with pytest.raises(errors.ServerError) as e:
            c.tags()
        assert str(e.value) == 'simulated error'

    @pytest.mark.parametrize(
        'ns,ids,expected', [
            (None, None, {}),
            ('default', None, {'ns': 'default'}),
            ('foo', None, {'ns': 'foo'}),
            (None, True, {'ids': 'True'}),
            (None, False, {'ids': 'False'}),
            (None, 'other', {'ids': 'other'}),
            ('default', False, {'ns': 'default', 'ids': 'False'}),
        ]
    )
    def test_tags_params(self, mocker, ns, ids, expected):
        mock_request = mocker.patch(
            'synse.client.HTTPClientV3.make_request',
            returns=requests.Response()
        )

        c = client.HTTPClientV3('localhost')
        _ = c.tags(ns=ns, ids=ids)

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            url='http://localhost:5000/v3/tags',
            method='get',
            params=expected,
        )

    def test_transaction(self, mock_response, synse_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/v3/transaction/123',
            json=synse_response.transaction,
        )

        c = client.HTTPClientV3('localhost')

        resp = c.transaction('123')

        assert isinstance(resp, models.TransactionStatus)
        assert resp.raw == synse_response.transaction

    def test_transaction_error(self, mock_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/v3/transaction/123',
            status=500,
            json={
                'context': 'simulated error',
            },
        )

        c = client.HTTPClientV3('localhost')

        with pytest.raises(errors.ServerError) as e:
            c.transaction('123')
        assert str(e.value) == 'simulated error'

    def test_transactions(self, mock_response, synse_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/v3/transaction',
            json=synse_response.transactions,
        )

        c = client.HTTPClientV3('localhost')

        resp = c.transactions()

        assert isinstance(resp, list)
        assert all(isinstance(elem, str) for elem in resp)

    def test_transactions_error(self, mock_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/v3/transaction',
            status=500,
            json={
                'context': 'simulated error',
            },
        )

        c = client.HTTPClientV3('localhost')

        with pytest.raises(errors.ServerError) as e:
            c.transactions()
        assert str(e.value) == 'simulated error'

    def test_version(self, mock_response, synse_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/version',
            json=synse_response.version,
        )

        c = client.HTTPClientV3('localhost')

        resp = c.version()

        assert isinstance(resp, models.Version)
        assert resp.raw == synse_response.version

    def test_version_error(self, mock_response):
        mock_response.add(
            method='GET',
            url='http://localhost:5000/version',
            status=500,
        )

        c = client.HTTPClientV3('localhost')

        with pytest.raises(errors.ServerError) as e:
            c.version()
        assert str(e.value) == ''  # no context means no message

    def test_write_async(self, mock_response, synse_response):
        mock_response.add(
            method='POST',
            url='http://localhost:5000/v3/write/123',
            json=synse_response.write_async,
        )

        c = client.HTTPClientV3('localhost')

        resp = c.write_async('123', {'action': 'foo'})

        assert isinstance(resp, list)
        assert all(isinstance(elem, models.TransactionInfo) for elem in resp)

    def test_write_async_error(self, mock_response):
        mock_response.add(
            method='POST',
            url='http://localhost:5000/v3/write/123',
            status=404,
            json={
                'context': 'device not found',
            },
        )

        c = client.HTTPClientV3('localhost')

        with pytest.raises(errors.NotFound) as e:
            c.write_async('123', {'action': 'foo'})
        assert str(e.value) == 'device not found'

    def test_write_sync(self, mock_response, synse_response):
        mock_response.add(
            method='POST',
            url='http://localhost:5000/v3/write/wait/123',
            json=synse_response.write_sync,
        )

        c = client.HTTPClientV3('localhost')

        resp = c.write_sync('123', {'action': 'foo'})

        assert isinstance(resp, list)
        assert all(isinstance(elem, models.TransactionStatus) for elem in resp)

    def test_write_sync_error(self, mock_response):
        mock_response.add(
            method='POST',
            url='http://localhost:5000/v3/write/wait/123',
            status=404,
            json={
                'context': 'device not found',
            },
        )

        c = client.HTTPClientV3('localhost')

        with pytest.raises(errors.NotFound) as e:
            c.write_sync('123', {'action': 'foo'})
        assert str(e.value) == 'device not found'
