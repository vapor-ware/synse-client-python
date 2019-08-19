"""Tests for the synse.client HTTP client implementation."""

import typing

import pytest

from synse import client, errors, models


class TestHTTPClientV3:
    """Tests for the HTTPClientV3 class."""

    @pytest.mark.asyncio
    async def test_init(self) -> None:
        c = client.HTTPClientV3('localhost')

        assert c.session is not None
        assert c.host == 'localhost'
        assert c.port == 5000
        assert c.base == 'http://localhost:5000'
        assert c.url == 'http://localhost:5000/v3'

    @pytest.mark.asyncio
    async def test_make_request_error(self) -> None:
        # The request will return a connection error (an instance of
        # RequestException) if the fetched URL doesn't hit a match.
        c = client.HTTPClientV3('localhost')

        with pytest.raises(errors.SynseError):
            await c.make_request(
                method='GET',
                url='http://localhost:5000/v3/bar',
            )

    async def test_config(self, test_client, synse_data) -> None:
        resp = await test_client.config()

        assert isinstance(resp, models.Config)
        assert resp.data == synse_data.config

    async def test_config_error(self, test_client_err) -> None:
        with pytest.raises(errors.ServerError) as e:
            await test_client_err.config()

        assert str(e.value) == 'error context'

    async def test_info(self, test_client, synse_data) -> None:
        resp = await test_client.info('123')

        assert isinstance(resp, models.DeviceInfo)
        assert resp._data == synse_data.info

    async def test_info_error(self, test_client_err) -> None:
        with pytest.raises(errors.ServerError) as e:
            await test_client_err.info('123')

        assert str(e.value) == 'error context'

    async def test_plugin(self, test_client, synse_data) -> None:
        resp = await test_client.plugin('123')

        assert isinstance(resp, models.PluginInfo)
        assert resp._data == synse_data.plugin

    async def test_plugin_error(self, test_client_err) -> None:
        with pytest.raises(errors.ServerError) as e:
            await test_client_err.plugin('123')

        assert str(e.value) == 'error context'

    async def test_plugin_health(self, test_client, synse_data) -> None:
        resp = await test_client.plugin_health()

        assert isinstance(resp, models.PluginHealth)
        assert resp._data == synse_data.plugin_health

    async def test_plugin_health_error(self, test_client_err) -> None:
        with pytest.raises(errors.ServerError) as e:
            await test_client_err.plugin_health()

        assert str(e.value) == 'error context'

    async def test_plugins(self, test_client, synse_data) -> None:
        resp = await test_client.plugins()

        assert isinstance(resp, list)
        assert all(isinstance(elem, models.PluginSummary) for elem in resp)
        assert all(elem._data == synse_data.plugins[i] for i, elem in enumerate(resp))

    async def test_plugins_error(self, test_client_err) -> None:
        with pytest.raises(errors.ServerError) as e:
            await test_client_err.plugins()

        assert str(e.value) == 'error context'

    async def test_read(self, test_client, synse_data) -> None:
        resp = await test_client.read()

        assert isinstance(resp, list)
        assert all(isinstance(elem, models.Reading) for elem in resp)
        assert all(elem._data == synse_data.read[i] for i, elem in enumerate(resp))

    async def test_read_error(self, test_client_err) -> None:
        with pytest.raises(errors.ServerError) as e:
            await test_client_err.read()

        assert str(e.value) == 'error context'

    #
    # @pytest.mark.asyncio
    # @pytest.mark.parametrize(
    #     'ns,tags,expected', [
    #         (None, None, {}),
    #         ('default', None, {'ns': 'default'}),
    #         ('foo', None, {'ns': 'foo'}),
    #         (None, ['vapor'], {'tags': 'vapor'}),
    #         ('foo', ['vapor'], {'ns': 'foo', 'tags': 'vapor'}),
    #         ('foo', ['vapor', 'a/b'], {'ns': 'foo', 'tags': 'vapor,a/b'}),
    #         ('foo', ['vapor', 'a/b', '1/2:3'], {'ns': 'foo', 'tags': 'vapor,a/b,1/2:3'}),
    #     ]
    # )
    # async def test_read_params(self, mocker, ns, tags, expected):
    #     mock_request = mocker.patch(
    #         'synse.client.HTTPClientV3.make_request',
    #         returns=requests.Response()
    #     )
    #
    #     c = client.HTTPClientV3('localhost')
    #     _ = await c.read(ns=ns, tags=tags)
    #
    #     mock_request.assert_called_once()
    #     mock_request.assert_called_with(
    #         url='http://localhost:5000/v3/read',
    #         method='get',
    #         params=expected,
    #     )

    async def test_read_cache(self, test_client):
        resp = test_client.read_cache()

        assert isinstance(resp, typing.AsyncGenerator)
        data = [r async for r in resp]
        assert len(data) == 3
        assert all(isinstance(elem, models.Reading) for elem in data)

    async def test_read_cache_error(self, test_client_err):
        resp = test_client_err.read_cache()

        assert isinstance(resp, typing.AsyncGenerator)
        with pytest.raises(errors.ServerError) as e:
            _ = [x async for x in resp]
        assert str(e.value) == 'error: handler err'

    # @pytest.mark.asyncio
    # @pytest.mark.parametrize(
    #     'start,end,expected', [
    #         (None, None, {}),
    #         ('timestamp-1', None, {'start': 'timestamp-1'}),
    #         (None, 'timestamp-1', {'end': 'timestamp-1'}),
    #         ('timestamp-1', 'timestamp-2', {'start': 'timestamp-1', 'end': 'timestamp-2'}),
    #     ]
    # )
    # async def test_read_cache_params(self, mocker, start, end, expected):
    #     mock_request = mocker.patch(
    #         'synse.client.HTTPClientV3.make_request',
    #         returns=requests.Response()
    #     )
    #
    #     c = client.HTTPClientV3('localhost')
    #     _ = [x for x in c.read_cache(start=start, end=end)]
    #
    #     mock_request.assert_called_once()
    #     mock_request.assert_called_with(
    #         url='http://localhost:5000/v3/readcache',
    #         method='get',
    #         stream=True,
    #         params=expected,
    #     )

    async def test_read_device(self, test_client, synse_data) -> None:
        resp = await test_client.read_device('123')

        assert isinstance(resp, list)
        assert all(isinstance(elem, models.Reading) for elem in resp)
        assert all(elem._data == synse_data.read_device[i] for i, elem in enumerate(resp))

    async def test_read_device_error(self, test_client_err) -> None:
        with pytest.raises(errors.ServerError) as e:
            await test_client_err.read_device('123')

        assert str(e.value) == 'error context'

    async def test_scan(self, test_client, synse_data) -> None:
        resp = await test_client.scan()

        assert isinstance(resp, list)
        assert all(isinstance(elem, models.DeviceSummary) for elem in resp)
        assert all(elem._data == synse_data.scan[i] for i, elem in enumerate(resp))

    async def test_scan_error(self, test_client_err) -> None:
        with pytest.raises(errors.ServerError) as e:
            await test_client_err.scan()

        assert str(e.value) == 'error context'

    # @pytest.mark.asyncio
    # @pytest.mark.parametrize(
    #     'force,ns,sort,tags,expected', [
    #         (None, None, None, None, {}),
    #         (False, None, None, None, {'force': 'False'}),
    #         (True, None, None, None, {'force': 'True'}),
    #         ('other', None, None, None, {'force': 'other'}),
    #         (None, 'default', None, None, {'ns': 'default'}),
    #         (None, 'foo', None, None, {'ns': 'foo'}),
    #         (None, None, 'id,type', None, {'sort': 'id,type'}),
    #         (None, None, 'id', None, {'sort': 'id'}),
    #         (None, None, None, ['vapor'], {'tags': 'vapor'}),
    #         (None, None, None, ['vapor', 'foo/bar'], {'tags': 'vapor,foo/bar'}),
    #         (None, None, None, ['vapor', 'foo/bar', 'a/b:c'], {'tags': 'vapor,foo/bar,a/b:c'}),
    #         (None, None, 'id,type', ['vapor', 'foo/bar', 'a/b:c'], {'sort': 'id,type', 'tags': 'vapor,foo/bar,a/b:c'}),
    #         (None, 'foo', 'id,type', ['vapor', 'foo/bar', 'a/b:c'], {'ns': 'foo', 'sort': 'id,type', 'tags': 'vapor,foo/bar,a/b:c'}),
    #         (True, 'foo', 'id,type', ['vapor', 'foo/bar', 'a/b:c'], {'force': 'True', 'ns': 'foo', 'sort': 'id,type', 'tags': 'vapor,foo/bar,a/b:c'}),
    #     ]
    # )
    # async def test_scan_params(self, mocker, force, ns, sort, tags, expected):
    #     mock_request = mocker.patch(
    #         'synse.client.HTTPClientV3.make_request',
    #         returns=requests.Response()
    #     )
    #
    #     c = client.HTTPClientV3('localhost')
    #     _ = await c.scan(force=force, ns=ns, sort=sort, tags=tags)
    #
    #     mock_request.assert_called_once()
    #     mock_request.assert_called_with(
    #         url='http://localhost:5000/v3/scan',
    #         method='get',
    #         params=expected,
    #     )

    async def test_status(self, test_client, synse_data) -> None:
        resp = await test_client.status()

        assert isinstance(resp, models.Status)
        assert resp._data == synse_data.status

    async def test_status_error(self, test_client_err) -> None:
        with pytest.raises(errors.ServerError) as e:
            await test_client_err.status()

        assert str(e.value) == 'error context'

    async def test_tags(self, test_client, synse_data) -> None:
        resp = await test_client.tags()

        assert isinstance(resp, list)
        assert all(isinstance(elem, str) for elem in resp)
        assert all(elem == synse_data.tags[i] for i, elem in enumerate(resp))

    async def test_tags_error(self, test_client_err) -> None:
        with pytest.raises(errors.ServerError) as e:
            await test_client_err.tags()

        assert str(e.value) == 'error context'

    # @pytest.mark.asyncio
    # @pytest.mark.parametrize(
    #     'ns,ids,expected', [
    #         (None, None, {}),
    #         ('default', None, {'ns': 'default'}),
    #         ('foo', None, {'ns': 'foo'}),
    #         (None, True, {'ids': 'True'}),
    #         (None, False, {'ids': 'False'}),
    #         (None, 'other', {'ids': 'other'}),
    #         ('default', False, {'ns': 'default', 'ids': 'False'}),
    #     ]
    # )
    # async def test_tags_params(self, mocker, ns, ids, expected):
    #     mock_request = mocker.patch(
    #         'synse.client.HTTPClientV3.make_request',
    #         returns=requests.Response()
    #     )
    #
    #     c = client.HTTPClientV3('localhost')
    #     _ = await c.tags(ns=ns, ids=ids)
    #
    #     mock_request.assert_called_once()
    #     mock_request.assert_called_with(
    #         url='http://localhost:5000/v3/tags',
    #         method='get',
    #         params=expected,
    #     )

    async def test_transaction(self, test_client, synse_data) -> None:
        resp = await test_client.transaction('123')

        assert isinstance(resp, models.TransactionStatus)
        assert resp._data == synse_data.transaction

    async def test_transaction_error(self, test_client_err) -> None:
        with pytest.raises(errors.ServerError) as e:
            await test_client_err.transaction('123')

        assert str(e.value) == 'error context'

    async def test_transactions(self, test_client, synse_data) -> None:
        resp = await test_client.transactions()

        assert isinstance(resp, list)
        assert all(isinstance(elem, str) for elem in resp)
        assert all(elem == synse_data.transactions[i] for i, elem in enumerate(resp))

    async def test_transactions_error(self, test_client_err) -> None:
        with pytest.raises(errors.ServerError) as e:
            await test_client_err.transactions()

        assert str(e.value) == 'error context'

    async def test_version(self, test_client, synse_data) -> None:
        resp = await test_client.version()

        assert isinstance(resp, models.Version)
        assert resp._data == synse_data.version

    async def test_version_error(self, test_client_err) -> None:
        with pytest.raises(errors.ServerError) as e:
            await test_client_err.version()

        assert str(e.value) == 'error context'

    async def test_write_async(self, test_client, synse_data) -> None:
        resp = await test_client.write_async('123', {'action': 'foo'})

        assert isinstance(resp, list)
        assert all(isinstance(elem, models.TransactionInfo) for elem in resp)
        assert all(elem._data == synse_data.write_async[i] for i, elem in enumerate(resp))

    async def test_write_async_error(self, test_client_err) -> None:
        with pytest.raises(errors.ServerError) as e:
            await test_client_err.write_async('123', {'action': 'foo'})

        assert str(e.value) == 'error context'

    async def test_write_sync(self, test_client, synse_data) -> None:
        resp = await test_client.write_sync('123', {'action': 'foo'})

        assert isinstance(resp, list)
        assert all(isinstance(elem, models.TransactionStatus) for elem in resp)
        assert all(elem._data == synse_data.write_sync[i] for i, elem in enumerate(resp))

    async def test_write_sync_error(self, test_client_err) -> None:
        with pytest.raises(errors.ServerError) as e:
            await test_client_err.write_sync('123', {'action': 'foo'})

        assert str(e.value) == 'error context'
