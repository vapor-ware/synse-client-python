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

```python

import asyncio
from synse import client


async def main():
    async with client.HTTPClientV3(host='localhost') as c:

        # Get the status
        resp = await c.status()
        print(f'Status:    {resp.status}')
        print(f'Timestamp: {resp.timestamp}')

        # Get all device IDs
        print('Devices:')
        for device in await c.scan():
            print(f' • {device.id}')

        # Read from all devices
        print('Readings:')
        for reading in await c.read():
            print('{:<15}{} {}'.format(
                reading.type,
                reading.value,
                reading.unit['symbol']if reading.unit else '',
            ))


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

```

Running the above prints the following:

```
Status:    ok
Timestamp: 2020-04-08 18:17:19+00:00
Devices:
 • 01976737-085c-5e4c-94bc-a383d3d130fb
 • 0570c34a-32fd-56c5-a0a3-d4a229e89536
 • 0da9a0cb-9d58-5ac7-8293-7c29485fa65f
 • 1b714cf2-cc56-5c36-9741-fd6a483b5f10
 • 494bd3ed-72ec-53e9-ba65-729610516e25
 • 51fe41da-7631-5984-a93e-bc544f31a6e9
 • 6944ec43-2dc5-5b3a-a934-8f3937d7e93d
 • 69c2e1e2-e658-5d71-8e43-091f68aa6e84
 • 89fd576d-462c-53be-bcb6-7870e70c304a
 • 9669ca7a-41c1-5ad8-8c45-c359ca47f7f4
 • 9907bdfa-75e1-5af5-8385-87184f356b22
 • 998e6025-ddfb-533a-9efe-dd26d512b555
 • a75917de-920c-59b0-9df3-7d95b4cc50f8
 • b079f4b8-42b8-5e62-8ee7-b74040a40561
 • b30f844d-f0db-557f-b073-893917f909ad
 • b9324904-385b-581d-b790-5e53eaabfd20
 • bc583d62-c9c9-5778-863b-0ebe360ebcb0
 • c2f6f762-fa30-5f0a-ba6c-f52d8deb3c07
 • d755b2a9-1df5-5202-ab9f-f9b928592e1a
 • dde22569-deea-5d06-a0a4-1320993c110a
 • e8525fdf-73f1-5e2b-aa45-17ad12199a49
 • f041883c-cf87-55d7-a978-3d3103836412
 • fef34490-4952-5e92-bf4d-aad169df980e
Readings:
status         locked 
temperature    6 C
direction      forward 
frequency      0 RPM
power          1919 W
power          2072 W
energy         680 kWh
state          off 
color          000000 
state          off 
color          000000 
state          ready 
status         stopped 
position       1 
power          1994 W
power          2003 W
energy         680 kWh
voltage        275 V
pressure       5 Pa
temperature    91 C
temperature    18 C
speed          40 mm/s
humidity       60 %
temperature    62 C
temperature    98 C
pressure       -2 Pa
temperature    6 C
power          2055 W
voltage        307 V
```

Note that while the client is async by default, individual commands may be
run synchronously when wrapped with the client's `sync` method, e.g.

```python
from synse import client

c = client.HTTPClientV3(host='localhost')

resp = c.sync(c.status())
```