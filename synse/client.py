"""HTTP API client for Synse Server."""

import logging

import requests
import requests.exceptions

from . import errors, responses

log = logging.getLogger('synse')

# HTTP Methods
GET = 'get'
POST = 'post'


class ApiClient(object):
    """The API client for Synse Server.

    Args:
        host (str): The hostname/IP address for the Synse Server instance.
        port (int): The port that Synse Server is listening on (default: 5000).
        session (requests.Session): A session for reusing connections (optional).
        timeout (int): The timeout (in seconds) for a request to Synse Server
            (default: 10s).
    """

    def __init__(self, host, port=5000, session=None, timeout=10):
        self.session = session if session is not None else requests.Session()
        self.host = host
        self.port = port
        self.timeout = timeout

        self._server_version = None

    def __str__(self):
        return '<Synse Client: {}:{}>'.format(self.host, self.port)

    def __repr__(self):
        return self.__str__()

    @property
    def server_version(self):
        """Get the API version of the Synse Server instance."""
        if not self._server_version:
            self._server_version = self.version().api_version
        return self._server_version

    # ------
    # UTIL
    # ------

    def _do_request(self, method, url, params=None, data=None):
        """Issue a request to Synse Server.

        Args:
            method (str):
            url (str):
            params ():
            data ():
        """

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                timeout=self.timeout,
            )
        except requests.exceptions.RequestException as e:
            # FIXME - better error handling.
            log.error('error while calling {}: {}', url, e)
            raise

        if response.status_code == 200:
            log.debug('ok')
            return response

        elif response.status_code == 400:
            log.error('400')
            # FIXME: collect json data as well.
            raise errors.InvalidInput(response)

        elif response.status_code == 404:
            log.error('404')
            raise errors.NotFound(response)

        elif response.status_code >= 500:
            log.error('500')
            raise errors.ServerError(response)

        else:
            raise errors.SynseError(response)

    def _url(self, path, versioned=True):
        """"""
        base = 'http://{}:{}/synse'.format(self.host, self.port)
        if versioned:
            base += '/{}'.format(self.server_version)

        if not path.startswith('/'):
            path = '/' + path
        return base + path

    # ------
    # API COMMANDS
    # ------

    def status(self):
        """"""
        path = '/test'

        return responses.Status(self._do_request(
            url=self._url(path, versioned=False),
            method=GET,
        ))

    def version(self):
        """"""
        path = '/version'

        return responses.Version(self._do_request(
            url=self._url(path, versioned=False),
            method=GET,
        ))

    def config(self):
        """"""
        path = '/config'
        raise NotImplementedError

    def capabilities(self):
        """"""
        path = '/capabilities'
        raise NotImplementedError

    def plugins(self):
        """"""
        path = '/plugins'
        raise NotImplementedError

    def scan(self):
        """"""
        path = '/scan'

        return responses.Scan(self._do_request(
            url=self._url(path),
            method=GET,
        ))

    def read(self):
        """"""
        path = '/read'
        raise NotImplementedError

    def write(self):
        """"""
        path = '/write'
        raise NotImplementedError

    def transaction(self):
        """"""
        path = '/transaction'
        raise NotImplementedError

    def info(self):
        """"""
        path = '/info'
        raise NotImplementedError
