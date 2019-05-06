
import pytest

from synse import client


class TestHTTPClientV3:
    """Tests for the HTTPClientV3 class."""

    def test_init(self):
        c = client.HTTPClientV3('localhost')

        assert c.session is not None
        assert c.host == 'localhost'
        assert c.port == 5000
        assert c.timeout == 10
        assert c.base == 'http://localhost:5000'
        assert c.url == 'http://localhost:5000/v3'
