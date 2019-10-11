
Tests
=====

Test environments are managed by `tox <https://tox.readthedocs.io/en/latest/>`_ and the
tests are run via `pytest <https://docs.pytest.org/en/latest/>`_.

Additionally, project formatting and linting may be executed in tox environments (``fmt`` and
``lint``, respectively) which use ``twine``, ``autopep8``, ``isort``, and ``flake8``.

Unit tests are found in the ``tests/unit`` directory. Similarly, integration tests are
found in the ``tests/integration`` directory. For convenience, Makefile targets are included
to run project tests.

Unit tests
----------

Unit tests may be run via ``tox``:

.. code-block:: bash

  $ tox tests/unit

or via ``make``:

.. code-block:: bash

  $ make test


Integration tests
-----------------

Integration tests require `docker-compose <https://docs.docker.com/compose/>`_, which is used
to spin up a local ephemeral instance of Synse Server and a connected emulator plugin. These
containers expose the API and data which the tests run against.

Integration tests may be run via ``tox``:

.. code-block:: bash

  $ docker-compose -f compose/integration.yaml rm -fsv
  $ docker-compose -f compose/integration.yaml up -d
  $ tox tests/integration
  $ docker-compose -f compose/integration.yaml down


or via ``make``:

.. code-block:: bash

  $ make integration
