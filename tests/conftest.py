
import pytest
import responses


class SynseTestData:
    """A class which holds response data for the Synse v3 HTTP API endpoints
    which can be used as test data.
    """

    config = {
        'logging': 'debug',
        'pretty_json': True,
        'locale': 'en_US',
        'plugin': {
            'tcp': [
                'emulator:5001'
            ],
            'unix': [

            ]
        },
        'cache': {
            'meta': {
                'ttl': 20
            },
            'transaction': {
                'ttl': 300
            }
        },
        'grpc': {
            'timeout': 3
        },
        'metrics': {
            'enabled': False
        }
    }

    status = {
        'status': 'ok',
        'timestamp': '2019-05-07T11:14:39Z'
    }

    version = {
        'version': '3.0.0',
        'api_version': 'v3'
    }

    plugins = [
        {
            'name': 'emulator plugin',
            'maintainer': 'vaporio',
            'tag': 'vaporio/emulator-plugin',
            'description': 'A plugin with emulated devices and data',
            'id': '4032ffbe-80db-5aa5-b794-f35c88dff85c',
            'active': True
        }
    ]

    plugin = {
        'name': 'emulator plugin',
        'maintainer': 'vaporio',
        'tag': 'vaporio/emulator-plugin',
        'description': 'A plugin with emulated devices and data',
        'vcs': 'github.com/vapor-ware/synse-emulator-plugin',
        'id': '4032ffbe-80db-5aa5-b794-f35c88dff85c',
        'active': True,
        'network': {
            'address': 'emulator:5001',
            'protocol': 'tcp'
        },
        'version': {
            'plugin_version': '3.0.0',
            'sdk_version': '3.0.0',
            'build_date': '2019-05-02T13:56:45',
            'git_commit': '1a1d95b',
            'git_tag': '2.4.5-5-g1a1d95b',
            'arch': 'amd64',
            'os': 'linux'
        },
        'health': {
            'timestamp': '2019-05-07T11:14:39Z',
            'status': 'OK',
            'checks': [
                {
                    'name': 'read queue health',
                    'status': 'OK',
                    'type': 'periodic',
                    'message': '',
                    'timestamp': ''
                },
                {
                    'name': 'write queue health',
                    'status': 'OK',
                    'type': 'periodic',
                    'message': '',
                    'timestamp': ''
                }
            ]
        }
    }

    plugin_health = {
        'status': 'healthy',
        'updated': '2019-05-07T11:14:39Z',
        'healthy': [
            '4032ffbe-80db-5aa5-b794-f35c88dff85c'
        ],
        'unhealthy': [

        ],
        'active': 1,
        'inactive': 0
    }

    scan = [
        {
            'id': '01976737-085c-5e4c-94bc-a383d3d130fb',
            'alias': 'emulator-backup-led',
            'info': 'Synse Backup LED',
            'type': 'led',
            'plugin': '4032ffbe-80db-5aa5-b794-f35c88dff85c',
            'tags': [
                'system/id:01976737-085c-5e4c-94bc-a383d3d130fb',
                'system/type:led'
            ]
        },
        {
            'id': '1b714cf2-cc56-5c36-9741-fd6a483b5f10',
            'alias': '',
            'info': 'Synse Door Lock',
            'type': 'lock',
            'plugin': '4032ffbe-80db-5aa5-b794-f35c88dff85c',
            'tags': [
                'system/id:1b714cf2-cc56-5c36-9741-fd6a483b5f10',
                'system/type:lock'
            ]
        },
        {
            'id': '494bd3ed-72ec-53e9-ba65-729610516e25',
            'alias': '',
            'info': 'Synse Pressure Sensor 2',
            'type': 'pressure',
            'plugin': '4032ffbe-80db-5aa5-b794-f35c88dff85c',
            'tags': [
                'system/id:494bd3ed-72ec-53e9-ba65-729610516e25',
                'system/type:pressure'
            ]
        },
    ]

    tags = [
        'system/id:01976737-085c-5e4c-94bc-a383d3d130fb',
        'system/id:1b714cf2-cc56-5c36-9741-fd6a483b5f10',
        'system/id:494bd3ed-72ec-53e9-ba65-729610516e25',
        'system/id:69c2e1e2-e658-5d71-8e43-091f68aa6e84',
        'system/id:89fd576d-462c-53be-bcb6-7870e70c304a',
        'system/id:9669ca7a-41c1-5ad8-8c45-c359ca47f7f4',
        'system/id:9907bdfa-75e1-5af5-8385-87184f356b22',
        'system/id:998e6025-ddfb-533a-9efe-dd26d512b555',
        'system/id:b30f844d-f0db-557f-b073-893917f909ad',
        'system/id:b9324904-385b-581d-b790-5e53eaabfd20',
        'system/id:c2f6f762-fa30-5f0a-ba6c-f52d8deb3c07',
        'system/id:f041883c-cf87-55d7-a978-3d3103836412',
        'system/id:fef34490-4952-5e92-bf4d-aad169df980e',
        'system/type:airflow',
        'system/type:fan',
        'system/type:humidity',
        'system/type:led',
        'system/type:lock',
        'system/type:pressure',
        'system/type:temperature'
    ]

    info = {
        'timestamp': '2019-05-07T11:14:24Z',
        'id': 'c2f6f762-fa30-5f0a-ba6c-f52d8deb3c07',
        'type': 'temperature',
        'plugin': '4032ffbe-80db-5aa5-b794-f35c88dff85c',
        'info': 'Synse Temperature Sensor 4',
        'metadata': {
            'model': 'emul8-temp'
        },
        'capabilities': {
            'mode': 'rw',
            'write': {
                'actions': [

                ]
            }
        },
        'tags': [
            'system/id:c2f6f762-fa30-5f0a-ba6c-f52d8deb3c07',
            'system/type:temperature'
        ],
        'outputs': [
            {
                'name': 'temperature',
                'type': 'temperature',
                'precision': 2,
                'unit': {
                    'name': 'celsius',
                    'symbol': 'C'
                },
                'scalingFactor': 0.0
            }
        ],
        'alias': '',
        'sort_index': 0
    }

    read = [
        {
            'device': '9907bdfa-75e1-5af5-8385-87184f356b22',
            'timestamp': '2019-05-07T11:14:40Z',
            'type': 'temperature',
            'device_type': 'temperature',
            'unit': {
                'name': 'celsius',
                'symbol': 'C'
            },
            'value': 21,
            'context': {

            }
        },
        {
            'device': '89fd576d-462c-53be-bcb6-7870e70c304a',
            'timestamp': '2019-05-07T11:14:40Z',
            'type': 'temperature',
            'device_type': 'temperature',
            'unit': {
                'name': 'celsius',
                'symbol': 'C'
            },
            'value': 27,
            'context': {

            }
        },
        {
            'device': 'b9324904-385b-581d-b790-5e53eaabfd20',
            'timestamp': '2019-05-07T11:14:40Z',
            'type': 'temperature',
            'device_type': 'temperature',
            'unit': {
                'name': 'celsius',
                'symbol': 'C'
            },
            'value': 12,
            'context': {

            }
        },
    ]

    read_cache = '{"device":"01976737-085c-5e4c-94bc-a383d3d130fb","timestamp":"2019-05-07T11:14:39Z","type":"state","device_type":"led","unit":null,"value":"off","context":{}}\n{"device":"01976737-085c-5e4c-94bc-a383d3d130fb","timestamp":"2019-05-07T11:14:39Z","type":"color","device_type":"led","unit":null,"value":"000000","context":{}}\n{"device":"b9324904-385b-581d-b790-5e53eaabfd20","timestamp":"2019-05-07T11:14:39Z","type":"temperature","device_type":"temperature","unit":{"name":"celsius","symbol":"C"},"value":58,"context":{}}'

    read_device = [
        {
            'device': 'c2f6f762-fa30-5f0a-ba6c-f52d8deb3c07',
            'timestamp': '2019-05-07T11:14:40Z',
            'type': 'temperature',
            'device_type': 'temperature',
            'unit': {
                'name': 'celsius',
                'symbol': 'C'
            },
            'value': 2,
            'context': {

            }
        }
    ]

    write_async = [
        {
            'id': '1234567890abcdef',
            'device': '01976737-085c-5e4c-94bc-a383d3d130fb',
            'context': {
                'action': 'color',
                'data': 'ZmYwMGZm',
                'transaction': '1234567890abcdef'
            },
            'timeout': '30s'
        }
    ]

    transactions = [
        '1234567890abcdef'
    ]

    transaction = {
        'id': '1234567890abcdef',
        'created': '2019-05-07T11:14:40Z',
        'updated': '2019-05-07T11:14:40Z',
        'timeout': '30s',
        'context': {
            'action': 'color',
            'data': 'ZmYwMGZm',
            'transaction': '1234567890abcdef'
        },
        'message': '',
        'status': 'PENDING',
        'device': '01976737-085c-5e4c-94bc-a383d3d130fb'
    }

    write_sync = [
        {
            'id': 'abcdef1234567890',
            'created': '2019-05-07T11:14:40Z',
            'updated': '2019-05-07T11:14:41Z',
            'timeout': '30s',
            'status': 'DONE',
            'context': {
                'action': 'color',
                'data': 'ZmYwMGZm',
                'transaction': 'abcdef1234567890'
            },
            'message': '',
            'device': '01976737-085c-5e4c-94bc-a383d3d130fb'
        }
    ]


@pytest.fixture(scope='module')
def synse_response():
    return SynseTestData()


@pytest.fixture()
def mock_response():
    with responses.RequestsMock() as rsps:
        yield rsps