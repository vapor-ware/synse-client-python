
Usage Overview
==============

To get started, you will need a running instance of Synse Server with a configured plugin
to provide device reading data. Below is a simple compose file which will bring up an
instance of Synse Server with the emulator plugin connected.

.. code-block:: yaml

  version: '3'
  services:
    synse-server:
      container_name: synse-server
      image: vaporio/synse-server
      ports:
      - '5000:5000'
      environment:
        SYNSE_PLUGIN_TCP: emulator-plugin:5001
      links:
      - emulator-plugin

    emulator-plugin:
      container_name: emulator-plugin
      image: vaporio/emulator-plugin
      expose:
      - '5001'


With the above compose file saved locally as ``docker-compose.yaml``, you can start the
simple deployment with:

.. code-block:: bash

  $ docker-compose up -d

Now, the Synse Server API can be reached at ``localhost:5000``.

The Synse Python client package provides a client for both the HTTP API and the WebSocket API.
The two APIs are largely similar and provide access to the same device data and control.

HTTP API
--------

Synse Server's HTTP API can be accessed using an HTTP client. Clients are versioned based on
the version of the Synse API they are compatible with, e.g. ``HTTPClientV3`` is compatible with
the Synse v3 API.

The client may be initialized and used directly, in which case it must be closed explicitly:

.. code-block:: python

  client = HTTPClientV3('localhost')
  ...
  await client.close()

It may also be used as a context manager, which will automatically close the session when the
context is exited:

.. code-block:: python

  async with HTTPClientV3('localhost') as client:
    ...

Example
~~~~~~~

Below is an example which creates a client, scans for all devices and for each LED device,
turns it on.

.. code-block:: python

  import asyncio

  from synse.client import HTTPClientV3


  async def main():
      """An example function which """

      c = HTTPClientV3(
          host='localhost',
          timeout=3,
      )

      for device in await c.scan():
          if device.type == 'led':
              status = await c.write_sync(
                  device=device.id,
                  payload={
                      'action': 'state',
                      'data': 'on',
                  }
              )

              for s in status:
                  assert s.status == 'DONE'

      await c.close()


  if __name__ == '__main__':
      loop = asyncio.get_event_loop()
      loop.run_until_complete(main())

Reference
~~~~~~~~~

.. autoclass:: synse.client.HTTPClientV3
  :members:
  :noindex:


WebSocket API
-------------

Synse Server's WebSocket API can be accessed using a WebSocket client. Clients are versioned based on
the version of the Synse API they are compatible with, e.g. ``WebsocketClientV3`` is compatible with
the Synse v3 API.

The client may be initialized and used directly, in which case it must be connected and closed explicitly:

.. code-block:: python

  client = WebsocketClientV3('localhost')
  await client.connect()
  ...
  await client.close()

It may also be used as a context manager, which will automatically connect and close the session when the
context is exited:

.. code-block:: python

  async with WebsocketClientV3('localhost') as client:
    ...

Example
~~~~~~~

Below is an example which creates a client, scans for all devices and for each LED device,
turns it on.

.. code-block:: python

  import asyncio

  from synse.client import WebsocketClientV3


  async def main():
      """An example function which """

      c = WebsocketClientV3(
          host='localhost',
      )
      await c.connect()

      for device in await c.scan():
          if device.type == 'led':
              status = await c.write_sync(
                  device=device.id,
                  payload={
                      'action': 'state',
                      'data': 'on',
                  }
              )

              for s in status:
                  assert s.status == 'DONE'

      await c.close()

  if __name__ == '__main__':
      loop = asyncio.get_event_loop()
      loop.run_until_complete(main())


Reference
~~~~~~~~~

.. autoclass:: synse.client.WebsocketClientV3
  :members:
  :noindex:

