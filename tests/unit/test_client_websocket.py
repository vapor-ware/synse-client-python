"""Tests for the synse.client WebSocket client implementation."""

import aiohttp
import asynctest
import pytest

from synse import client, errors, models


@pytest.mark.asyncio
class TestWebsocketClientV3:
    """Tests for the WebsocketClientV3 class."""

    async def test_init(self) -> None:
        c = client.WebsocketClientV3('localhost')

        assert c.host == 'localhost'
        assert c.port == 5000
        assert c.api_version == 'v3'
        assert c.connect_url == 'ws://localhost:5000/v3/connect'
        assert isinstance(c.session, aiohttp.ClientSession)

    async def test_str(self) -> None:
        c = client.WebsocketClientV3('localhost')

        assert str(c) == '<Synse WebSocket Client (v3): localhost:5000>'
        assert str([c]) == '[<Synse WebSocket Client (v3): localhost:5000>]'

    async def test_context(self) -> None:
        c = client.WebsocketClientV3('localhost')

        with pytest.raises(TypeError):
            with c:
                pass

    async def test_async_context(self) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.connect') as mock_connect:
            def se(*_):
                c._connection = 'test sentinel'
            mock_connect.side_effect = se

            c = client.WebsocketClientV3('localhost')
            assert c._connection is None

            async with c:
                pass

            assert c._connection == 'test sentinel'

        mock_connect.assert_called_once()

    async def test_connection_ok(self):
        # Get the connection via property when it exists.
        c = client.WebsocketClientV3('localhost')
        c._connection = 'foo'

        assert c.connection == 'foo'

    async def test_connection_error(self):
        # Get the connection via property when it does not exist.
        c = client.WebsocketClientV3('localhost')

        with pytest.raises(RuntimeError):
            _ = c.connection

    async def test_make_request_error(self) -> None:
        # The request will return a connection error if the fetched URL
        # isn't valid. This should be wrapped in a Synse error.
        c = client.WebsocketClientV3('127.0.0.1', 5432)

        with pytest.raises(errors.SynseError):
            await c.connect()

    async def test_config(self, synse_data) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.return_value = {'data': synse_data.config}

            c = client.WebsocketClientV3('localhost')
            resp = await c.config()

            assert isinstance(resp, models.Config)
            assert resp.data == synse_data.config

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/config',
        )

    async def test_config_error(self) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.side_effect = ValueError('simulated error')

            c = client.WebsocketClientV3('localhost')

            with pytest.raises(ValueError):
                await c.config()

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/config',
        )

    async def test_info(self, synse_data) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.return_value = {'data': synse_data.info}

            c = client.WebsocketClientV3('localhost')
            resp = await c.info('123')

            assert isinstance(resp, models.DeviceInfo)
            assert resp._data == synse_data.info

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/info',
            data={
                'device': '123',
            },
        )

    async def test_info_error(self) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.side_effect = ValueError('simulated error')

            c = client.WebsocketClientV3('localhost')

            with pytest.raises(ValueError):
                await c.info('123')

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/info',
            data={
                'device': '123',
            },
        )

    async def test_plugin(self, synse_data) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.return_value = {'data': synse_data.plugin}

            c = client.WebsocketClientV3('localhost')
            resp = await c.plugin('123')

            assert isinstance(resp, models.PluginInfo)
            assert resp._data == synse_data.plugin

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/plugin',
            data={
                'plugin': '123',
            },
        )

    async def test_plugin_error(self) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.side_effect = ValueError('simulated error')

            c = client.WebsocketClientV3('localhost')

            with pytest.raises(ValueError):
                await c.plugin('123')

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/plugin',
            data={
                'plugin': '123',
            },
        )

    async def test_plugin_health(self, synse_data) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.return_value = {'data': synse_data.plugin_health}

            c = client.WebsocketClientV3('localhost')
            resp = await c.plugin_health()

            assert isinstance(resp, models.PluginHealth)
            assert resp._data == synse_data.plugin_health

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/plugin_health',
        )

    async def test_plugin_health_error(self) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.side_effect = ValueError('simulated error')

            c = client.WebsocketClientV3('localhost')

            with pytest.raises(ValueError):
                await c.plugin_health()

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/plugin_health',
        )

    async def test_plugins(self, synse_data) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.return_value = {'data': synse_data.plugins}

            c = client.WebsocketClientV3('localhost')
            resp = await c.plugins()

            assert isinstance(resp, list)
            assert all(isinstance(elem, models.PluginSummary) for elem in resp)

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/plugins',
            data={},
        )

    async def test_plugins_error(self) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.side_effect = ValueError('simulated error')

            c = client.WebsocketClientV3('localhost')

            with pytest.raises(ValueError):
                await c.plugins()

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/plugins',
            data={},
        )

    @pytest.mark.parametrize(
        'ns,tags,expected', [
            (None, None, {}),
            ('default', None, {'ns': 'default'}),
            (None, [], {'tags': []}),
            (None, ['foo', 'default/bar'], {'tags': ['foo', 'default/bar']}),
            ('default', ['foo', 'default/bar'], {'ns': 'default', 'tags': ['foo', 'default/bar']}),
        ]
    )
    async def test_read(self, synse_data, ns, tags, expected) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.return_value = {'data': synse_data.read}

            c = client.WebsocketClientV3('localhost')
            resp = await c.read(
                ns=ns,
                tags=tags,
            )

            assert isinstance(resp, list)
            assert all(isinstance(elem, models.Reading) for elem in resp)

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/read',
            data=expected,
        )

    async def test_read_error(self) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.side_effect = ValueError('simulated error')

            c = client.WebsocketClientV3('localhost')

            with pytest.raises(ValueError):
                await c.read()

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/read',
            data={},
        )

    @pytest.mark.parametrize(
        'start,end,expected', [
            (None, None, {}),
            ('2019-04-22T13:30:00Z', None, {'start': '2019-04-22T13:30:00Z'}),
            (None, '2019-04-22T13:30:00Z', {'end': '2019-04-22T13:30:00Z'}),
            ('2019-04-22T13:30:00Z', '2019-04-22T13:30:00Z', {'start': '2019-04-22T13:30:00Z', 'end': '2019-04-22T13:30:00Z'}),
        ]
    )
    async def test_read_cache(self, synse_data, start, end, expected) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.return_value = {'data': synse_data.read}

            c = client.WebsocketClientV3('localhost')
            resp = [x async for x in c.read_cache(
                start=start,
                end=end,
            )]

            assert isinstance(resp, list)
            assert all(isinstance(elem, models.Reading) for elem in resp)

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/read_cache',
            data=expected,
        )

    async def test_read_cache_error(self) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.side_effect = ValueError('simulated error')

            c = client.WebsocketClientV3('localhost')

            with pytest.raises(ValueError):
                _ = [x async for x in c.read_cache()]

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/read_cache',
            data={},
        )

    async def test_read_device(self, synse_data) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.return_value = {'data': synse_data.read_device}

            c = client.WebsocketClientV3('localhost')
            resp = await c.read_device('123')

            assert isinstance(resp, list)
            assert all(isinstance(elem, models.Reading) for elem in resp)

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/read_device',
            data={
                'device': '123',
            },
        )

    async def test_read_device_error(self) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.side_effect = ValueError('simulated error')

            c = client.WebsocketClientV3('localhost')

            with pytest.raises(ValueError):
                await c.read_device('123')

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/read_device',
            data={
                'device': '123',
            },
        )

    @pytest.mark.parametrize(
        'force,ns,tags,expected', [
            (None, None, None, {}),
            (True, None, None, {'force': True}),
            (None, 'default', None, {'ns': 'default'}),
            (None, None, [], {'tags': []}),
            (None, None, ['foo', 'default/bar'], {'tags': ['foo', 'default/bar']}),
            (False, 'default', ['foo', 'default/bar'], {'force': False, 'ns': 'default', 'tags': ['foo', 'default/bar']}),
        ]
    )
    async def test_scan(self, synse_data, force, ns, tags, expected) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.return_value = {'data': synse_data.scan}

            c = client.WebsocketClientV3('localhost')
            resp = await c.scan(
                force=force,
                ns=ns,
                tags=tags,
            )

            assert isinstance(resp, list)
            assert all(isinstance(elem, models.DeviceSummary) for elem in resp)

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/scan',
            data=expected,
        )

    async def test_scan_error(self) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.side_effect = ValueError('simulated error')

            c = client.WebsocketClientV3('localhost')

            with pytest.raises(ValueError):
                await c.scan()

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/scan',
            data={},
        )

    async def test_status(self, synse_data) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.return_value = {'data': synse_data.status}

            c = client.WebsocketClientV3('localhost')
            resp = await c.status()

            assert isinstance(resp, models.Status)
            assert resp._data == synse_data.status

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/status',
        )

    async def test_status_error(self) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.side_effect = ValueError('simulated error')

            c = client.WebsocketClientV3('localhost')

            with pytest.raises(ValueError):
                await c.status()

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/status',
        )

    @pytest.mark.parametrize(
        'ns,ids,expected', [
            (None, None, {}),
            ('default', None, {'ns': 'default'}),
            (None, True, {'ids': True}),
            ('default', False, {'ns': 'default', 'ids': False}),
        ]
    )
    async def test_tags(self, synse_data, ns, ids, expected) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.return_value = {'data': synse_data.tags}

            c = client.WebsocketClientV3('localhost')
            resp = await c.tags(
                ns=ns,
                ids=ids,
            )

            assert isinstance(resp, list)
            assert all(isinstance(elem, str) for elem in resp)

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/tags',
            data=expected,
        )

    async def test_tags_error(self) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.side_effect = ValueError('simulated error')

            c = client.WebsocketClientV3('localhost')

            with pytest.raises(ValueError):
                await c.tags()

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/tags',
            data={},
        )

    async def test_transaction(self, synse_data) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.return_value = {'data': synse_data.transaction}

            c = client.WebsocketClientV3('localhost')
            resp = await c.transaction('123')

            assert isinstance(resp, models.TransactionStatus)
            assert resp._data == synse_data.transaction

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/transaction',
            data={
                'transaction': '123',
            },
        )

    async def test_transaction_error(self) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.side_effect = ValueError('simulated error')

            c = client.WebsocketClientV3('localhost')

            with pytest.raises(ValueError):
                await c.transaction('123')

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/transaction',
            data={
                'transaction': '123',
            },
        )

    async def test_transactions(self, synse_data) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.return_value = {'data': synse_data.transactions}

            c = client.WebsocketClientV3('localhost')
            resp = await c.transactions()

            assert isinstance(resp, list)
            assert all(isinstance(elem, str) for elem in resp)

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/transactions',
        )

    async def test_transactions_error(self) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.side_effect = ValueError('simulated error')

            c = client.WebsocketClientV3('localhost')

            with pytest.raises(ValueError):
                await c.transactions()

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/transactions',
        )

    async def test_version(self, synse_data) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.return_value = {'data': synse_data.version}

            c = client.WebsocketClientV3('localhost')
            resp = await c.version()

            assert isinstance(resp, models.Version)
            assert resp._data == synse_data.version

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/version',
        )

    async def test_version_error(self) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.side_effect = ValueError('simulated error')

            c = client.WebsocketClientV3('localhost')

            with pytest.raises(ValueError):
                await c.version()

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/version',
        )

    async def test_write_async(self, synse_data) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.return_value = {'data': synse_data.write_async}

            c = client.WebsocketClientV3('localhost')
            resp = await c.write_async('123', {'action': 'foo'})

            assert isinstance(resp, list)
            assert all(isinstance(elem, models.TransactionInfo) for elem in resp)

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/write_async',
            data={
                'device': '123',
                'payload': {
                    'action': 'foo',
                },
            },
        )

    async def test_write_async_error(self) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.side_effect = ValueError('simulated error')

            c = client.WebsocketClientV3('localhost')

            with pytest.raises(ValueError):
                await c.write_async('123', {'action': 'foo'})

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/write_async',
            data={
                'device': '123',
                'payload': {
                    'action': 'foo',
                },
            },
        )

    async def test_write_sync(self, synse_data) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.return_value = {'data': synse_data.write_sync}

            c = client.WebsocketClientV3('localhost')
            resp = await c.write_sync('123', {'action': 'foo'})

            assert isinstance(resp, list)
            assert all(isinstance(elem, models.TransactionStatus) for elem in resp)

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/write_sync',
            data={
                'device': '123',
                'payload': {
                    'action': 'foo',
                },
            },
        )

    async def test_write_sync_error(self) -> None:
        with asynctest.patch('synse.client.WebsocketClientV3.request') as mock_request:
            mock_request.side_effect = ValueError('simulated error')

            c = client.WebsocketClientV3('localhost')

            with pytest.raises(ValueError):
                await c.write_sync('123', {'action': 'foo'})

        mock_request.assert_called_once()
        mock_request.assert_called_with(
            'request/write_sync',
            data={
                'device': '123',
                'payload': {
                    'action': 'foo',
                },
            },
        )
