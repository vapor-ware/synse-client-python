
import typing

import pytest

from synse import errors, models
from synse.client import HTTPClientV3

# Since we define our own test config, and device IDs & plugin ID
# are deterministic, the IDs should not change and are thus well-known.
plugin_id = '4032ffbe-80db-5aa5-b794-f35c88dff85c'
device_led = 'f041883c-cf87-55d7-a978-3d3103836412'
device_temp_1 = '9907bdfa-75e1-5af5-8385-87184f356b22'
device_temp_2 = '89fd576d-462c-53be-bcb6-7870e70c304a'
device_temp_3 = 'b9324904-385b-581d-b790-5e53eaabfd20'
device_temp_4 = 'c2f6f762-fa30-5f0a-ba6c-f52d8deb3c07'

# Well-known transaction ids for testing.
txn_id_1 = '0000001'
txn_id_2 = '0000002'
txn_id_3 = '0000003'
txn_id_4 = '0000004'


def new_client(host='localhost', port=5000):
    """Create a new HTTP client for tests.

    This can't be done as a fixture since the aiohttp client
    needs to be created with the event loop running, which will
    not be the case at startup.
    """
    return HTTPClientV3(
        host=host,
        port=port,
    )


class TestConfig:

    async def test_ok(self):
        resp = await new_client().config()

        # We don't need to check the entirety of the returned configuration,
        # we just want to know we got something and it generally seems right.
        assert len(resp.data) != 0
        assert 'logging' in resp.data
        assert 'plugin' in resp.data
        assert 'cache' in resp.data

    async def test_connect_error(self):
        with pytest.raises(errors.SynseError):
            await new_client('192.3.3.111').config()


class TestInfo:

    async def test_ok(self):
        resp = await new_client().info(device_temp_1)

        assert isinstance(resp, models.DeviceInfo)
        assert resp.id == device_temp_1
        assert resp.type == 'temperature'
        assert resp.info == 'Synse Temperature Sensor 1'
        assert resp.plugin == plugin_id
        assert resp.tags == [
            'foo/bar',
            f'system/id:{device_temp_1}',
            f'system/type:temperature',
        ]

    async def test_connect_error(self):
        with pytest.raises(errors.SynseError):
            await new_client('192.3.3.111').info(device_temp_1)

    async def test_not_found_error(self):
        with pytest.raises(errors.NotFound):
            await new_client().info('111-222-333')


class TestPlugin:

    async def test_ok(self):
        resp = await new_client().plugin(plugin_id)

        assert isinstance(resp, models.PluginInfo)
        assert resp.id == plugin_id
        assert resp.name == 'emulator plugin'
        assert resp.tag == 'vaporio/emulator-plugin'

    async def test_connect_error(self):
        with pytest.raises(errors.SynseError):
            await new_client('192.3.3.111').plugin(plugin_id)

    async def test_not_found_error(self):
        with pytest.raises(errors.NotFound):
            await new_client().plugin('111-222-333')


class TestPlugins:

    async def test_ok(self):
        resp = await new_client().plugins()

        assert isinstance(resp, list)
        assert len(resp) == 1

        plugin = resp[0]
        assert isinstance(plugin, models.PluginSummary)
        assert plugin.id == plugin_id
        assert plugin.name == 'emulator plugin'
        assert plugin.tag == 'vaporio/emulator-plugin'

    async def test_connect_error(self):
        with pytest.raises(errors.SynseError):
            await new_client('192.3.3.111').plugins()


class TestPluginHealth:

    async def test_ok(self):
        resp = await new_client().plugin_health()

        assert isinstance(resp, models.PluginHealth)
        assert resp.status == 'healthy'
        assert resp.healthy == [
            plugin_id,
        ]
        assert resp.unhealthy == []
        assert resp.active == 1
        assert resp.inactive == 0

    async def test_connect_error(self):
        with pytest.raises(errors.SynseError):
            await new_client('192.3.3.111').plugin_health()


class TestRead:

    async def test_ok(self):
        expected = (
            device_led,
            device_temp_1,
            device_temp_2,
            device_temp_3,
            device_temp_4,
        )

        resp = await new_client().read()

        assert isinstance(resp, list)
        assert len(resp) == 6  # 1 reading per temp device, 2 per led device

        led_count, temp_count, devices = 0, 0, set()
        for reading in resp:
            devices.add(reading.device)
            if reading.device_type == 'temperature':
                temp_count += 1
            elif reading.device_type == 'led':
                led_count += 1
            else:
                pytest.fail('unexpected reading device type in response')

        assert led_count == 2
        assert temp_count == 4
        assert len(expected) == len(devices)
        for dev in expected:
            assert dev in devices

    async def test_ok_single_tag_multiple_matches(self):
        expected = (
            device_led,
            device_temp_1,
            device_temp_2,
        )

        resp = await new_client().read(tags=[
            'foo/bar'
        ])

        assert isinstance(resp, list)
        assert len(resp) == 4  # 1 reading per temp device, 2 per led device

        led_count, temp_count, devices = 0, 0, set()
        for reading in resp:
            devices.add(reading.device)
            if reading.device_type == 'temperature':
                temp_count += 1
            elif reading.device_type == 'led':
                led_count += 1
            else:
                pytest.fail('unexpected reading device type in response')

        assert led_count == 2
        assert temp_count == 2
        assert len(expected) == len(devices)
        for dev in expected:
            assert dev in devices

    async def test_ok_single_tag_single_match(self):
        expected = (
            device_temp_3,
        )

        resp = await new_client().read(tags=[
            f'system/id:{device_temp_3}',
        ])

        assert isinstance(resp, list)
        assert len(resp) == 1  # 1 reading per temp device, 2 per led device

        led_count, temp_count, devices = 0, 0, set()
        for reading in resp:
            devices.add(reading.device)
            if reading.device_type == 'temperature':
                temp_count += 1
            elif reading.device_type == 'led':
                led_count += 1
            else:
                pytest.fail('unexpected reading device type in response')

        assert led_count == 0
        assert temp_count == 1
        assert len(expected) == len(devices)
        for dev in expected:
            assert dev in devices

    async def test_ok_multiple_tags_multiple_matches(self):
        expected = (
            device_temp_1,
            device_temp_2,
        )

        resp = await new_client().read(tags=[
            'foo/bar',
            'system/type:temperature',
        ])

        assert isinstance(resp, list)
        assert len(resp) == 2  # 1 reading per temp device, 2 per led device

        led_count, temp_count, devices = 0, 0, set()
        for reading in resp:
            devices.add(reading.device)
            if reading.device_type == 'temperature':
                temp_count += 1
            elif reading.device_type == 'led':
                led_count += 1
            else:
                pytest.fail('unexpected reading device type in response')

        assert led_count == 0
        assert temp_count == 2
        assert len(expected) == len(devices)
        for dev in expected:
            assert dev in devices

    async def test_ok_multiple_tags_single_match(self):
        expected = (
            device_led,
        )

        resp = await new_client().read(tags=[
            'foo/bar',
            'system/type:led',
        ])

        assert isinstance(resp, list)
        assert len(resp) == 2  # 1 reading per temp device, 2 per led device

        led_count, temp_count, devices = 0, 0, set()
        for reading in resp:
            devices.add(reading.device)
            if reading.device_type == 'temperature':
                temp_count += 1
            elif reading.device_type == 'led':
                led_count += 1
            else:
                pytest.fail('unexpected reading device type in response')

        assert led_count == 2
        assert temp_count == 0
        assert len(expected) == len(devices)
        for dev in expected:
            assert dev in devices

    async def test_ok_multiple_tag_groups_match(self):
        expected = (
            device_led,
            device_temp_1,
            device_temp_2,
            device_temp_4,
        )

        resp = await new_client().read(tags=[
            ['foo/bar'],
            [f'system/id:{device_temp_4}'],
        ])

        assert isinstance(resp, list)
        assert len(resp) == 5  # 1 reading per temp device, 2 per led device

        led_count, temp_count, devices = 0, 0, set()
        for reading in resp:
            devices.add(reading.device)
            if reading.device_type == 'temperature':
                temp_count += 1
            elif reading.device_type == 'led':
                led_count += 1
            else:
                pytest.fail('unexpected reading device type in response')

        assert led_count == 2
        assert temp_count == 3
        assert len(expected) == len(devices)
        for dev in expected:
            assert dev in devices

    async def test_ok_single_tag_no_match(self):
        resp = await new_client().read(tags=[
            'not-a-tag',
        ])

        assert isinstance(resp, list)
        assert len(resp) == 0

    async def test_ok_multiple_tags_no_match(self):
        resp = await new_client().read(tags=[
            'foo/bar',
            f'system/id:{device_temp_4}',
        ])

        assert isinstance(resp, list)
        assert len(resp) == 0

    async def test_ok_multiple_tag_groups_no_match(self):
        resp = await new_client().read(tags=[
            [
                'foo/bar',
                f'system/id:{device_temp_4}',
            ],
            [
                'not-a-tag',
            ],
        ])

        assert isinstance(resp, list)
        assert len(resp) == 0

    async def test_connect_error(self):
        with pytest.raises(errors.SynseError):
            await new_client('192.3.3.111').read()


class TestReadCache:

    async def test_ok(self):
        resp = new_client().read_cache()

        assert isinstance(resp, typing.AsyncGenerator)
        data = [d async for d in resp]
        assert len(data) != 0

    async def test_connect_error(self):
        with pytest.raises(errors.SynseError):
            [x async for x in new_client('192.3.3.111').read_cache()]


class TestReadDevice:

    async def test_ok(self):
        resp = await new_client().read_device(device_temp_2)

        assert isinstance(resp, list)
        assert len(resp) == 1

        reading = resp[0]
        assert reading.device == device_temp_2
        assert reading.type == 'temperature'
        assert reading.device_type == 'temperature'
        assert reading.context == {}
        assert reading.unit == {
            'symbol': 'C',
            'name': "celsius",
        }
        assert reading.value is not None

    async def test_connect_error(self):
        with pytest.raises(errors.SynseError):
            await new_client('192.3.3.111').read_device(device_temp_2)

    async def test_not_found_error(self):
        with pytest.raises(errors.NotFound):
            await new_client().read_device('111-222-333')


class TestScan:

    async def test_ok(self):
        expected = (
            device_led,
            device_temp_1,
            device_temp_2,
            device_temp_3,
            device_temp_4,
        )

        resp = await new_client().scan()

        assert isinstance(resp, list)
        assert len(resp) == 5
        for item in resp:
            assert isinstance(item, models.DeviceSummary)
            assert item.id in expected
            assert item.type in ('temperature', 'led')

    async def test_ok_with_tags(self):
        expected = (
            device_led,
            device_temp_1,
            device_temp_2,
        )

        resp = await new_client().scan(
            tags=['foo/bar'],
        )

        assert isinstance(resp, list)
        assert len(resp) == 3
        for item in resp:
            assert isinstance(item, models.DeviceSummary)
            assert item.id in expected
            assert item.type in ('temperature', 'led')

    async def test_ok_with_multiple_tag_groups(self):
        expected = (
            device_led,
            device_temp_1,
            device_temp_2,
            device_temp_4,
        )

        resp = await new_client().scan(
            tags=[
                ['foo/bar'],
                [f'system/id:{device_temp_4}'],
            ]
        )

        assert isinstance(resp, list)
        assert len(resp) == 4
        for item in resp:
            assert isinstance(item, models.DeviceSummary)
            assert item.id in expected
            assert item.type in ('temperature', 'led')

    async def test_connect_error(self):
        with pytest.raises(errors.SynseError):
            await new_client('192.3.3.111').scan()


class TestStatus:

    async def test_ok(self):
        resp = await new_client().status()

        assert isinstance(resp, models.Status)
        assert resp.status == 'ok'
        assert resp.timestamp != ''

    async def test_connect_error(self):
        with pytest.raises(errors.SynseError):
            await new_client('192.3.3.111').status()


class TestTags:

    async def test_ok(self):
        expected = [
            'foo/bar',
            'system/type:temperature',
            'system/type:led',
        ]

        resp = await new_client().tags()

        assert isinstance(resp, list)
        assert len(resp) == 3
        for item in expected:
            assert item in resp

    async def test_ok_with_ids(self):
        expected = [
            'foo/bar',
            'system/type:temperature',
            'system/type:led',
            f'system/id:{device_led}',
            f'system/id:{device_temp_1}',
            f'system/id:{device_temp_2}',
            f'system/id:{device_temp_3}',
            f'system/id:{device_temp_4}',
        ]

        resp = await new_client().tags(ids=True)

        assert isinstance(resp, list)
        assert len(resp) == 8
        for item in expected:
            assert item in resp

    async def test_connect_error(self):
        with pytest.raises(errors.SynseError):
            await new_client('192.3.3.111').tags()


class TestVersion:

    async def test_ok(self):
        resp = await new_client().version()

        assert isinstance(resp, models.Version)
        assert resp.version != ''
        assert resp.api_version == 'v3'

    async def test_connect_error(self):
        with pytest.raises(errors.SynseError):
            await new_client('192.3.3.111').version()


class TestWriteAsync:

    async def test_ok(self):
        resp = await new_client().write_async(
            device=device_led,
            payload={
                'action': 'state',
                'data': 'on',
                'transaction': txn_id_1,
            },
        )

        assert isinstance(resp, list)
        assert len(resp) == 1

        info = resp[0]
        assert isinstance(info, models.TransactionInfo)
        assert info.id == txn_id_1
        assert info.device == device_led
        assert info.timeout == '30s'
        assert info.context == {
            'action': 'state',
            'data': 'on',
            'transaction': txn_id_1,
        }

    async def test_connect_error(self):
        with pytest.raises(errors.SynseError):
            await new_client('192.3.3.111').write_async(
                device=device_led,
                payload={
                    'action': 'state',
                    'data': 'on',
                },
            )

    async def test_not_found_error(self):
        with pytest.raises(errors.NotFound):
            await new_client().write_async(
                device='111-222-333',
                payload={
                    'action': 'state',
                    'data': 'on',
                },
            )

    async def test_bad_data(self):
        resp = await new_client().write_async(
            device=device_led,
            payload={
                'action': 'bad-action',
                'data': 'on',
                'transaction': txn_id_3,
            },
        )

        assert isinstance(resp, list)
        assert len(resp) == 1

        info = resp[0]
        assert isinstance(info, models.TransactionInfo)
        assert info.id == txn_id_3
        assert info.device == device_led
        assert info.timeout == '30s'
        assert info.context == {
            'action': 'bad-action',
            'data': 'on',
            'transaction': txn_id_3,
        }


class TestWriteSync:

    async def test_ok(self):
        resp = await new_client().write_sync(
            device=device_led,
            payload={
                'action': 'state',
                'data': 'on',
                'transaction': txn_id_2,
            },
        )

        assert isinstance(resp, list)
        assert len(resp) == 1

        status = resp[0]
        assert isinstance(status, models.TransactionStatus)
        assert status.id == txn_id_2
        assert status.device == device_led
        assert status.timeout == '30s'
        assert status.status == 'DONE'
        assert status.context == {
            'action': 'state',
            'data': 'on',
            'transaction': txn_id_2,
        }

    async def test_connect_error(self):
        with pytest.raises(errors.SynseError):
            await new_client('192.3.3.111').write_sync(
                device=device_led,
                payload={
                    'action': 'state',
                    'data': 'on',
                },
            )

    async def test_not_found_error(self):
        with pytest.raises(errors.NotFound):
            await new_client().write_sync(
                device='111-222-333',
                payload={
                    'action': 'state',
                    'data': 'on',
                },
            )

    async def test_bad_data(self):
        resp = await new_client().write_sync(
            device=device_led,
            payload={
                'action': 'bad-action',
                'data': 'on',
                'transaction': txn_id_4,
            },
        )

        assert isinstance(resp, list)
        assert len(resp) == 1

        status = resp[0]
        assert isinstance(status, models.TransactionStatus)
        assert status.id == txn_id_4
        assert status.device == device_led
        assert status.timeout == '30s'
        assert status.status == 'ERROR'
        assert status.context == {
            'action': 'bad-action',
            'data': 'on',
            'transaction': txn_id_4,
        }


class TestTransaction:

    async def test_ok(self):
        resp = await new_client().transaction(txn_id_1)

        assert isinstance(resp, models.TransactionStatus)
        assert resp.id == txn_id_1
        assert resp.device == device_led
        assert resp.timeout == '30s'
        assert resp.status == 'DONE'
        assert resp.context == {
            'action': 'state',
            'data': 'on',
            'transaction': txn_id_1,
        }

    async def test_connect_error(self):
        with pytest.raises(errors.SynseError):
            await new_client('192.3.3.111').transaction('123')

    async def test_not_found_error(self):
        with pytest.raises(errors.NotFound):
            await new_client().transaction('111-222-333')


class TestTransactions:

    async def test_ok(self):
        expected = [
            txn_id_1,
            txn_id_2,
            txn_id_3,
            txn_id_4,
        ]

        resp = await new_client().transactions()

        assert isinstance(resp, list)
        assert len(resp) == 4
        for txn in resp:
            assert txn in expected

    async def test_connect_error(self):
        with pytest.raises(errors.SynseError):
            await new_client('192.3.3.111').transactions()
