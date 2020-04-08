
Synse Python Client
===================

The official Python client for `Synse Server <https://github.com/vapor-ware/synse-server>`_.
This client allows programmatic access to the Synse Server API through a simple asynchronous
interface. To get started with Synse, see the `platform documentation <https://synse.readthedocs.io>`_.

.. code-block:: python

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


Installing
----------

The latest version of the Synse Python client can be installed with ``pip``:

.. code-block:: bash

   $ pip install synse


Features
--------

- Asynchronous API requests
- HTTP API client
- WebSocket API client
- Custom errors for simpler exception handling
- Response objects so you don't have to deal with JSON


Feedback
--------

Feedback for the Synse Python client is greatly appreciated! If you experience any issues, find the
documentation unclear, have feature requests, or just have questions about it, we’d love to know.
Feel free to open an issue on `GitHub <https://github.com/vapor-ware/synse-client-python/issues>`_
with any feedback you may have. If you are reporting a bug, please provide as much context as you can.


.. toctree::
   :hidden:
   :maxdepth: 2

   usage
   tests
   api_reference
   license
