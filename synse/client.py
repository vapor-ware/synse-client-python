"""HTTP API client for Synse Server."""

import logging
import json
from typing import Generator, Iterable

import requests
import requests.exceptions

from synse import errors, models

log = logging.getLogger('synse')

# HTTP Methods
GET = 'get'
POST = 'post'


class HTTPClientV3:
    """An HTTP client for Synse Server's v3 API.

    Args:
        host (str): The hostname/IP address for the Synse Server instance.
        port (int): The port that Synse Server is listening on. (default: 5000)
        session (requests.Session): A session for reusing connections.
        timeout (int): The timeout (in seconds) for a request to Synse Server.
            (default: 10s)
    """

    # The HTTPClientV3 uses the Synse v3 API.
    api_version = 'v3'

    def __init__(self, host, port=5000, session=None, timeout=10):
        self.session = session or requests.Session()
        self.host = host
        self.port = port
        self.timeout = timeout

        # TODO: tls
        self.base = f'http://{host}:{port}'
        self.url = f'{self.base}/{self.api_version}'

    def __str__(self):
        return f'<Synse HTTP Client ({self.api_version}): {self.host}:{self.port}>'

    def __repr__(self):
        return self.__str__()

    def make_request(self, method: str, url: str, params=None, data=None, **kwargs) -> requests.Response:
        """A helper method to issue a request to the configured Synse Server instance.

        This method is intended to only be used internally by the client. If
        finer-grained control over a request is desired, the client user may choose
        to use this method over the defined API methods.

        Returns:
            requests.Response: The response to the API request.

        Raises:
            errors.SynseError: An instance of a SynseError, wrapping any other error
            which may have occurred. An error will be raised if the client fails to
            make the request (e.g. connection issue, timeout, etc), or if the response
            has a non-2XX status code.
        """

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                timeout=self.timeout,
                **kwargs,
            )
        except requests.exceptions.RequestException as e:
            log.error(f'failed to issue request {method.upper()} {url}: {e}')
            raise errors.SynseError from e

        errors.wrap_and_raise_for_error(response)

        return response

    def config(self) -> models.Config:
        """Get the unified configuration for the Synse Server instance.

        Returns:
            The Synse v3 API config response.
        """

        response = self.make_request(
            url=f'{self.url}/config',
            method=GET,
        )
        return models.Config(response)

    def info(self, device) -> models.DeviceInfo:
        """Get all information associated with the specified device.

        Args:
            device (str): The ID of the device to get information for.

        Returns:
            The Synse v3 API info response.
        """

        response = self.make_request(
            url=f'{self.url}/info/{device}',
            method=GET,
        )
        return models.DeviceInfo(response)

    def plugin(self, plugin_id) -> models.PluginInfo:
        """Get all information associated with the specified plugin.

        Args:
            plugin_id (str): The ID of the plugin to get information for.

        Returns:
            The Synse v3 API plugin response.
        """

        response = self.make_request(
            url=f'{self.url}/plugin/{plugin_id}',
            method=GET,
        )
        return models.PluginInfo(response)

    def plugin_health(self) -> models.PluginHealth:
        """Get a summary of the health of all currently registered plugins.

        Returns:
            The Synse v3 API plugin health response.
        """

        response = self.make_request(
            url=f'{self.url}/plugin/health',
            method=GET,
        )
        return models.PluginHealth(response)

    def plugins(self) -> Iterable[models.PluginSummary]:
        """Get a summary of all plugins currently registered with the Synse Server instance.

        Returns:
            The Synse v3 API plugins response.
        """

        response = self.make_request(
            url=f'{self.url}/plugin',
            method=GET,
        )
        return [models.PluginSummary(response, raw) for raw in response.json()]

    def read(self, ns=None, tags=None) -> Iterable[models.Reading]:
        """Get the latest reading(s) for all devices which match the specified selector(s).

        Args:
            ns (str): The default namespace to use for the tags which do not
                include a namespace. (default: default)
            tags (list[str]): The tags to filter devices on.

        Returns:
            The Synse v3 API read response.
        """

        params = {
            'ns': ns,
            'tags': ','.join(tags) if tags else None
        }
        params = {k: v for k, v in params if v is not None}

        response = self.make_request(
            url=f'{self.url}/read',
            method=GET,
            params=params,
        )
        return [models.Reading(response, raw) for raw in response.json()]

    def read_cache(self, start=None, end=None) -> Generator[models.Reading]:
        """Get a window of cached device readings.

        Args:
            start (str): An RFC3339 formatted timestamp which specifies a starting
                bound on the cache data to return. If no timestamp is specified,
                there will not be a starting bound.
            end (str): An RFC3339 formatted timestamp which specifies an ending
                bound on the cache data to return. If no timestamp is specified,
                there will not be an ending bound.

        Yields:
            The Synse v3 API read cache response.
        """

        params = {
            'start': start,
            'end': end,
        }
        params = {k: v for k, v in params if v is not None}

        response = self.make_request(
            url=f'{self.url}/readcache',
            method=GET,
            stream=True,
            params=params,
        )

        for chunk in response.iter_lines():
            raw = json.loads(chunk)
            yield models.Reading(response, raw)

    def read_device(self, device) -> Iterable[models.Reading]:
        """Get the latest reading(s) for the specified device.

        Args:
            device (str): The ID of the device to get readings for.

        Returns:
            The Synse v3 API read device response.
        """

        response = self.make_request(
            url=f'{self.url}/read/{device}',
            method=GET,
        )
        return [models.Reading(response, raw) for raw in response.json()]

    def scan(self, force=None, ns=None, sort=None, tags=None) -> Generator[models.DeviceSummary]:
        """Get a summary of all devices currently exposed by the Synse Server instance.

        Args:
            force (bool): Force a re-scan (do not use the cache). If True, the
                request will take longer since the internal device cache will
                be rebuilt. Forcing a scan will ensure the set of returned devices
                is up-to-date.
            ns (str): The default namespace to use for the tags which do not
                include a namespace. (default: default)
            sort (str): Specify the fields to sort by. Multiple fields may be
                specified as a comma-separated string, e.g. "plugin,id". The
                "tags" field can not be used for sorting. (default:
                "plugin,sort_index,id", where the sort_index is an internal sort
                preference which a plugin can optionally specify.)
            tags (list[str]): The tags to filter devices on.

        Returns:
            The Synse v3 API scan response.
        """

        params = {
            'force': str(force) if force is not None else None,
            'ns': ns,
            'sort': sort,
            'tags': ','.join(tags) if tags else None
        }
        params = {k: v for k, v in params if v is not None}

        response = self.make_request(
            url=f'{self.url}/scan',
            method=GET,
            params=params,
        )
        return (models.DeviceSummary(response, raw) for raw in response.json())

    def status(self) -> models.Status:
        """Check the availability and connectivity status of the Synse Server instance.

        If the instance is reachable, this request will resolve; otherwise, it will
        raise an error.

        Returns:
            The Synse v3 API status response.
        """

        response = self.make_request(
            url=f'{self.base}/test',
            method=GET,
        )
        return models.Status(response)

    def tags(self, ns=None, ids=None) -> Iterable[str]:
        """Get a list of the tags currently associated with registered devices.

        Args:
            ns (str): The tag namespace(s) to use when searching for tags.
                (default: default)
            ids (bool): Include ID tags in the response. (default: false)

        Returns:
            The Synse v3 API tags response.
        """

        params = {
            'ns': ns,
            'ids': str(ids) if ids is not None else None,
        }
        params = {k: v for k, v in params if v is not None}

        response = self.make_request(
            url=f'{self.url}/tags',
            method=GET,
            params=params,
        )
        return response.json()

    def transaction(self, transaction_id) -> models.TransactionStatus:
        """Get the status of an asynchronous write transaction.

        Args:
            transaction_id (str): The ID of the transaction to get the status of.

        Returns:
            The Synse v3 API transaction response.
        """

        response = self.make_request(
            url=f'{self.url}/transaction/{transaction_id}',
            method=GET,
        )
        return models.TransactionStatus(response)

    def transactions(self) -> Iterable[str]:
        """Get a list of the transactions currently tracked by Synse.

        Returns:
            The Synse v3 API transactions response.
        """

        response = self.make_request(
            url=f'{self.url}/transaction',
            method=GET,
        )
        return response.json()

    def version(self) -> models.Version:
        """Get the version information for the configured Synse Server instance.

        Returns:
            The Synse v3 API version response.
        """

        response = self.make_request(
            url=f'{self.base}/version',
            method=GET,
        )
        return models.Version(response)

    def write_async(self, device, payload) -> Iterable[models.TransactionInfo]:
        """Write to the specified device asynchronously.

        This method will queue up a write with the device's plugin and will
        immediately return information for the transaction associated with
        the write. This transaction can be checked later to ensure the write
        completed successfully.

        Args:
            device (str): The ID of the device to write to.
            payload (list[dict] | dict): The write payload.

        Returns:
            The Synse v3 API asynchronous write response.
        """

        response = self.make_request(
            url=f'{self.url}/write/{device}',
            method=POST,
            data=payload,
        )
        return [models.TransactionInfo(response, raw) for raw in response.json()]

    def write_sync(self, device, payload) -> Iterable[models.TransactionStatus]:
        """Write to the specified device synchronously.

        This method will wait until the write action has completed. It is up
        to the caller to ensure that a suitable timeout is set for the request.

        Args:
            device (str): The ID of the device to write to.
            payload (list[dict] | dict): The write payload.

        Returns:
            The Synse v3 API synchronous write response.
        """

        response = self.make_request(
            url=f'{self.url}/write/wait/{device}',
            method=GET,
            data=payload,
        )
        return [models.TransactionStatus(response, raw) for raw in response.json()]


class WebsocketClientV3:
    """"""

    api_version = 'v3'

    def __str__(self):
        return f'<Synse WebSocket Client ({self.api_version}): >'
