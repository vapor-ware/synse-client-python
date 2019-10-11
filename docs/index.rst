
Synse Python Client
===================

The official Python client for `Synse Server <https://github.com/vapor-ware/synse-server>`_.
This client allows programmatic access to the Synse Server API through a simple asynchronous
interface. To get started with Synse, see the `platform documentation <https://synse.readthedocs.io>`_.

.. code-block:: python

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
