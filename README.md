# Synse Client (Python)

The official Python client for the [Synse](https://github.com/vapor-ware/synse) API.

This package provides clients for [Synse Server's](https://github.com/vapor-ware/synse-server)
HTTP and WebSocket API, making it easy to control and manage physical and virtual devices
and infrastructure from Python.

## Installation

The Synse Python client package can be installed with `pip`:

```
pip install synse
```

## Compatibility

Below is a table describing the compatibility of Synse python client versions with Synse platform versions.

|                            | Synse v2 | Synse v3 |
| -------------------------- | -------- | -------- |
| *synse* python client v1.x | ✗        | ✓        |

## Documentation

> https://synse-client-python.readthedocs.io

In addition to the hosted documentation, the package source code is well-commented,
providing basic information on client capabilities and the Synse data model.

For more information on the Synse platform, see the
[Synse Documentation](https://synse.readthedocs.io).

## Example

Below is a basic example of using the HTTP API, showcasing getting the server status,
getting the devices managed by the server, and reading from devices.

```python console
>>> from synse import client
>>> c = client.HTTPClientV3(host='localhost')
>>>
>>> # Get the status
>>> resp = c.status()
>>> resp.status
'ok'
>>> resp.timestamp
datetime.datetime(2019, 6, 3, 13, 47, 25, tzinfo=datetime.timezone.utc)
>>>
>>> # Get all device IDs
>>> for device in c.scan():
... 	print(device.id)
... 
'01976737-085c-5e4c-94bc-a383d3d130fb'
'1b714cf2-cc56-5c36-9741-fd6a483b5f10'
'494bd3ed-72ec-53e9-ba65-729610516e25'
'69c2e1e2-e658-5d71-8e43-091f68aa6e84'
'89fd576d-462c-53be-bcb6-7870e70c304a'
'9669ca7a-41c1-5ad8-8c45-c359ca47f7f4'
'9907bdfa-75e1-5af5-8385-87184f356b22'
'998e6025-ddfb-533a-9efe-dd26d512b555'
'b30f844d-f0db-557f-b073-893917f909ad'
'b9324904-385b-581d-b790-5e53eaabfd20'
'c2f6f762-fa30-5f0a-ba6c-f52d8deb3c07'
'f041883c-cf87-55d7-a978-3d3103836412'
'fef34490-4952-5e92-bf4d-aad169df980e'
>>>
>>> # Read from all devices
>>> for reading in c.read():
...     print('{:<15}{} {}'.format(
...         reading.type,
...         reading.value,
...         reading.unit['symbol'] if reading.unit else '',
...     ))
... 
pressure       2 Pa
temperature    75 C
airflow        39 mm/s
pressure       -4 Pa
temperature    27 C
temperature    3 C
airflow        0 mm/s
status         locked 
humidity       35 %
temperature    40 C
state          off 
color          000000 
state          off 
color          000000 
temperature    34 C
temperature    6 C
```
