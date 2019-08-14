"""API clients for the Synse Server API."""

import asyncio
import itertools
import json
import logging
from typing import Any, Generator, Iterable, List, Mapping, Optional, Union

import aiohttp

from synse import errors, models

log = logging.getLogger('synse')

# HTTP Methods
GET = 'get'
POST = 'post'


class HTTPClientV3:
    """An HTTP client for Synse Server's v3 API.

    Args:
        host: The hostname/IP address for the Synse Server instance.
        port: The port that Synse Server is listening on. (default: 5000)
        session: A session for reusing connections.
        timeout: The timeout (in seconds) for a request to Synse Server. (default: 10s)
        loop: The event loop to use for the client.
    """

    # The HTTPClientV3 uses the Synse v3 API.
    api_version = 'v3'

    def __init__(
            self,
            host: str,
            port: Optional[int] = 5000,
            timeout: Optional[float] = 10,
            session: Optional[aiohttp.ClientSession] = None,
            loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:

        self.loop = loop or asyncio.get_event_loop()
        self.host = host
        self.port = port
        self.session = session or aiohttp.ClientSession(
            loop=self.loop,
            timeout=aiohttp.ClientTimeout(
                total=timeout,
            ),
        )

        # TODO: tls
        self.base = f'http://{host}:{port}'
        self.url = f'{self.base}/{self.api_version}'

    def __str__(self):
        return f'<Synse HTTP Client ({self.api_version}): {self.host}:{self.port}>'

    def __repr__(self):
        return self.__str__()

    def sync(self, coro):
        """Run an asynchronous API call synchronously by wrapping it with this function.

        Examples:
            r = client.sync(client.status())
        """
        # TODO need to figure out how to do this

        return self.loop.run_until_complete(coro)

    async def make_request(
            self,
            method: str,
            url: str,
            params: Optional[Mapping[str, str]] = None,
            data: Any = None,
            **kwargs,
    ) -> Union[dict, list]:
        """A helper method to issue a request to the configured Synse Server instance.

        This method is intended to only be used internally by the client. If
        finer-grained control over a request is desired, the client user may choose
        to use this method over the defined API methods.

        Returns:
            The JSON response data marshaled into its Python type (dict or list).

        Raises:
            errors.SynseError: An instance of a SynseError, wrapping any other error
            which may have occurred. An error will be raised if the client fails to
            make the request (e.g. connection issue, timeout, etc), or if the response
            has a non-2XX status code.
        """

        try:
            async with self.session as session:
                async with session.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    **kwargs,
                ) as resp:

                    await errors.wrap_and_raise_for_error(resp)
                    return await resp.json()

        except aiohttp.ClientError as e:
            log.error(f'failed to issue request {method.upper()} {url} -> {e}')
            raise errors.SynseError from e

    async def config(self) -> models.Config:
        """Get the unified configuration for the Synse Server instance.

        Returns:
            The Synse v3 API config response.

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#config
        """

        response = await self.make_request(
            url=f'{self.url}/config',
            method=GET,
        )
        return models.make_response(
            models.Config,
            response,
        )

    async def info(self, device: str) -> models.DeviceInfo:
        """Get all information associated with the specified device.

        Args:
            device (str): The ID of the device to get information for.

        Returns:
            The Synse v3 API info response.

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#info
        """

        response = await self.make_request(
            url=f'{self.url}/info/{device}',
            method=GET,
        )
        return models.make_response(
            models.DeviceInfo,
            response,
        )

    async def plugin(self, plugin_id: str) -> models.PluginInfo:
        """Get all information associated with the specified plugin.

        Args:
            plugin_id (str): The ID of the plugin to get information for.

        Returns:
            The Synse v3 API plugin response.

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#plugin-info
        """

        response = await self.make_request(
            url=f'{self.url}/plugin/{plugin_id}',
            method=GET,
        )
        return models.make_response(
            models.PluginInfo,
            response,
        )

    async def plugin_health(self) -> models.PluginHealth:
        """Get a summary of the health of all currently registered plugins.

        Returns:
            The Synse v3 API plugin health response.

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#plugin-health
        """

        response = await self.make_request(
            url=f'{self.url}/plugin/health',
            method=GET,
        )
        return models.make_response(
            models.PluginHealth,
            response,
        )

    async def plugins(self) -> Iterable[models.PluginSummary]:
        """Get a summary of all plugins currently registered with the Synse Server instance.

        Returns:
            The Synse v3 API plugins response.

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#plugins
        """

        response = await self.make_request(
            url=f'{self.url}/plugin',
            method=GET,
        )
        return models.make_response(
            models.PluginSummary,
            response,
        )

    async def read(self, ns: str = None, tags: List[str] = None) -> Iterable[models.Reading]:
        """Get the latest reading(s) for all devices which match the specified selector(s).

        Args:
            ns (str): The default namespace to use for the tags which do not
                include a namespace. (default: default)
            tags (list[str]): The tags to filter devices on.

        Returns:
            The Synse v3 API read response.

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#read
        """

        params = {
            'ns': ns,
            'tags': ','.join(tags) if tags else None,
        }
        params = {k: v for k, v in params.items() if v is not None}

        response = await self.make_request(
            url=f'{self.url}/read',
            method=GET,
            params=params,
        )
        return models.make_response(
            models.Reading,
            response,
        )

    async def read_cache(self, start: str = None, end: str = None) -> Generator[models.Reading, None, None]:
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

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#read-cache
        """

        params = {
            'start': start,
            'end': end,
        }
        params = {k: v for k, v in params.items() if v is not None}

        response = await self.make_request(
            url=f'{self.url}/readcache',
            method=GET,
            stream=True,
            params=params,
        )

        # TODO: need to update read_cache for aiohttp
        for chunk in response.iter_lines():
            raw = json.loads(chunk)
            yield models.Reading(response, raw)

    async def read_device(self, device: str) -> Iterable[models.Reading]:
        """Get the latest reading(s) for the specified device.

        Args:
            device (str): The ID of the device to get readings for.

        Returns:
            The Synse v3 API read device response.

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#read-device
        """

        response = await self.make_request(
            url=f'{self.url}/read/{device}',
            method=GET,
        )
        return models.make_response(
            models.Reading,
            response,
        )

    async def scan(
            self, force: bool = None, ns: str = None, sort: str = None, tags: List[str] = None,
    ) -> List[models.DeviceSummary]:
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

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#scan
        """

        params = {
            'force': str(force) if force is not None else None,
            'ns': ns,
            'sort': sort,
            'tags': ','.join(tags) if tags else None,
        }
        params = {k: v for k, v in params.items() if v is not None}

        response = await self.make_request(
            url=f'{self.url}/scan',
            method=GET,
            params=params,
        )
        return models.make_response(
            models.DeviceSummary,
            response,
        )

    async def status(self) -> models.Status:
        """Check the availability and connectivity status of the Synse Server instance.

        If the instance is reachable, this request will resolve; otherwise, it will
        raise an error.

        Returns:
            The Synse v3 API status response.

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#test
        """

        response = await self.make_request(
            url=f'{self.base}/test',
            method=GET,
        )
        return models.make_response(
            models.Status,
            response,
        )

    async def tags(self, ns: str = None, ids: bool = None) -> Iterable[str]:
        """Get a list of the tags currently associated with registered devices.

        Args:
            ns (str): The tag namespace(s) to use when searching for tags.
                (default: default)
            ids (bool): Include ID tags in the response. (default: false)

        Returns:
            The Synse v3 API tags response.

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#tags
        """

        params = {
            'ns': ns,
            'ids': str(ids) if ids is not None else None,
        }
        params = {k: v for k, v in params.items() if v is not None}

        response = await self.make_request(
            url=f'{self.url}/tags',
            method=GET,
            params=params,
        )
        return models.make_response(
            None,
            response,
        )

    async def transaction(self, transaction_id: str) -> models.TransactionStatus:
        """Get the status of an asynchronous write transaction.

        Args:
            transaction_id (str): The ID of the transaction to get the status of.

        Returns:
            The Synse v3 API transaction response.

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#transaction
        """

        response = await self.make_request(
            url=f'{self.url}/transaction/{transaction_id}',
            method=GET,
        )
        return models.make_response(
            models.TransactionStatus,
            response,
        )

    async def transactions(self) -> Iterable[str]:
        """Get a list of the transactions currently tracked by Synse.

        Returns:
            The Synse v3 API transactions response.

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#transactions
        """

        response = await self.make_request(
            url=f'{self.url}/transaction',
            method=GET,
        )
        return models.make_response(
            None,
            response,
        )

    async def version(self) -> models.Version:
        """Get the version information for the configured Synse Server instance.

        Returns:
            The Synse v3 API version response.

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#version
        """

        response = await self.make_request(
            url=f'{self.base}/version',
            method=GET,
        )
        return models.make_response(
            models.Version,
            response,
        )

    async def write_async(
            self, device: str, payload: Union[List[dict], dict],
    ) -> Iterable[models.TransactionInfo]:
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

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#write-asynchronous
        """

        response = await self.make_request(
            url=f'{self.url}/write/{device}',
            method=POST,
            data=payload,
        )
        return models.make_response(
            models.TransactionInfo,
            response,
        )

    async def write_sync(
            self, device: str, payload: Union[List[dict], dict],
    ) -> Iterable[models.TransactionStatus]:
        """Write to the specified device synchronously.

        This method will wait until the write action has completed. It is up
        to the caller to ensure that a suitable timeout is set for the request.

        Args:
            device (str): The ID of the device to write to.
            payload (list[dict] | dict): The write payload.

        Returns:
            The Synse v3 API synchronous write response.

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#write-synchronous
        """

        response = await self.make_request(
            url=f'{self.url}/write/wait/{device}',
            method=POST,
            data=payload,
        )
        return models.make_response(
            models.TransactionStatus,
            response,
        )


# class WSSession:
#     """A class which models a WebSocket 'session'.
#
#     For the Synse API, each WebSocket message is sent with an ID which allows it
#     to match requests to responses. Each session is in charge of managing the
#     request IDs for sent events. By default, each client will have its own session.
#     """
#
#     def __init__(self, host, port, api_version):
#         self.host = host
#         self.port = port
#         self.api_version = api_version
#
#         self.connect_url = f'ws://{host}:{port}/{api_version}/connect'
#         self._id = itertools.count()
#         self._lock = asyncio.Lock()
#
#     async def _next(self):
#         async with self._lock:
#             return next(self._id)
#
#     async def request(self, event, data=None):
#         try:
#             async with websockets.connect(self.connect_url) as ws:
#                 message = {
#                     'id': await self._next(),
#                     'event': event,
#                 }
#                 if data:
#                     message['data'] = data
#
#                 await ws.send(json.dumps(message))
#
#                 response = await ws.recv()
#                 print(f'response ({type(response)}): {response}')
#                 return json.loads(response)
#         except ConnectionError as e:
#             log.error(f'failed to issue request {event} {self.host}:{self.port} -> {e}')
#             raise errors.SynseError from e


class WebsocketClientV3:
    """A WebSocket client for Synse Server's v3 API.

    Args:
        host: The hostname/IP address for the Synse Server instance.
        port: The port that Synse Server is listening on. (default: 5000)
        session: A session for reusing connections.
        loop: The event loop to use for the client.
    """

    api_version = 'v3'

    def __init__(
            self,
            host: str,
            port: Optional[int] = 5000,
            session: Optional[aiohttp.ClientSession] = None,
            loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:

        self.loop = loop or asyncio.get_event_loop()
        self.host = host
        self.port = port
        self.session = session or aiohttp.ClientSession(
            loop=self.loop,
        )

        self.connect_url = f'http://{host}:{port}/{self.api_version}/connect'

        # The WebSocket connection to use. This is created lazily whenever the first
        # call is made. It should be accessed by the `ws` property.
        self._ws = None

        self._id_iter = itertools.count()
        self._id_lock = asyncio.Lock()

    def __str__(self):
        return f'<Synse WebSocket Client ({self.api_version}): {self.host}:{self.port}>'

    def __repr__(self):
        return self.__str__()

    async def _next_id(self):
        """Get the next message ID number."""
        async with self._id_lock:
            return next(self._id_iter)

    async def ws(self):
        """Get the WebSocket connection."""
        if self._ws is None:
            self._ws = await self.session.ws_connect(
                url=self.connect_url,
            )
        return self._ws

    async def request(self, event, data=None):
        """"""
        ws = await self.ws()
        req = {
            'id': await self._next_id(),
            'event': event,
        }
        if data:
            req['data'] = data

        await ws.send(json.dumps(req))

        resp = await ws.receive()
        if resp.type == aiohttp.WSMsgType.text:
            return resp.json()
        elif resp.type == aiohttp.WSMsgType.closed:
            raise errors.SynseError('WebSocket connection closed: {}'.format(resp.extra))
        elif resp.type == aiohttp.WSMsgType.error:
            raise errors.SynseError('WebSocket error: {} : {}'.format(resp.data, resp.extra))

    async def config(self) -> models.Config:
        """Get the unified configuration for the Synse Server instance.

        Returns:
            The Synse v3 API config response.

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#config
        """

        r = await self.request('request/config')
        return models.make_response(
            models.Config,
            r['data'],
        )

    async def info(self, device: str) -> models.DeviceInfo:
        """Get all information associated with the specified device.

        Args:
            device (str): The ID of the device to get information for.

        Returns:
            The Synse v3 API info response.

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#info
        """

        r = await self.request('request/info', data={
            'device': device,
        })
        return models.make_response(
            models.DeviceInfo,
            r['data'],
        )

    async def plugin(self, plugin_id: str) -> models.PluginInfo:
        """Get all information associated with the specified plugin.

        Args:
            plugin_id (str): The ID of the plugin to get information for.

        Returns:
            The Synse v3 API plugin response.

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#plugin-info
        """

        r = await self.request('request/plugin', data={
            'plugin': plugin_id,
        })
        return models.make_response(
            models.PluginInfo,
            r['data'],
        )

    async def plugin_health(self) -> models.PluginHealth:
        """Get a summary of the health of all currently registered plugins.

        Returns:
            The Synse v3 API plugin health response.

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#plugin-health
        """

        r = await self.request('request/plugin_health')
        return models.make_response(
            models.PluginHealth,
            r['data'],
        )

    async def plugins(self) -> Iterable[models.PluginSummary]:
        """Get a summary of all plugins currently registered with the Synse Server instance.

        Returns:
            The Synse v3 API plugins response.

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#plugins
        """

        r = await self.request('request/plugins', data={})
        return models.make_response(
            models.PluginSummary,
            r['data'],
        )

    async def read(self, ns: str = None, tags: List[str] = None) -> Iterable[models.Reading]:
        """Get the latest reading(s) for all devices which match the specified selector(s).

        Args:
            ns (str): The default namespace to use for the tags which do not
                include a namespace. (default: default)
            tags (list[str]): The tags to filter devices on.

        Returns:
            The Synse v3 API read response.

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#read
        """

        data = {
            'ns': ns,
            'tags': tags,
        }
        data = {k: v for k, v in data.items() if v is not None}

        r = await self.request('request/read', data=data)
        return models.make_response(
            models.Reading,
            r['data'],
        )

    async def read_cache(self, start: str = None, end: str = None) -> Generator[models.Reading, None, None]:
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

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#read-cache
        """

        data = {
            'start': start,
            'end': end,
        }
        data = {k: v for k, v in data.items() if v is not None}

        r = await self.request('request/read_cache', data=data)
        for raw in r['data']:
            yield models.Reading(data=raw)

    async def read_device(self, device: str) -> Iterable[models.Reading]:
        """Get the latest reading(s) for the specified device.

        Args:
            device (str): The ID of the device to get readings for.

        Returns:
            The Synse v3 API read device response.

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#read-device
        """

        r = await self.request('request/read_device', data={
            'device': device,
        })
        return models.make_response(
            models.Reading,
            r['data'],
        )

    async def scan(
            self, force: bool = None, ns: str = None, sort: str = None, tags: List[str] = None,
    ) -> Generator[models.DeviceSummary, None, None]:
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

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#scan
        """

        data = {
            'force': force,
            'ns': ns,
            'sort': sort,
            'tags': tags,
        }
        data = {k: v for k, v in data.items() if v is not None}

        r = await self.request('request/scan', data=data)
        return models.make_response(
            models.DeviceSummary,
            r['data'],
        )

    async def status(self) -> models.Status:
        """Check the availability and connectivity status of the Synse Server instance.

        If the instance is reachable, this request will resolve; otherwise, it will
        raise an error.

        Returns:
            The Synse v3 API status response.

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#test
        """

        r = await self.request('request/status')
        return models.make_response(
            models.Status,
            r['data'],
        )

    async def tags(self, ns: str = None, ids: bool = None) -> Iterable[str]:
        """Get a list of the tags currently associated with registered devices.

        Args:
            ns (str): The tag namespace(s) to use when searching for tags.
                (default: default)
            ids (bool): Include ID tags in the response. (default: false)

        Returns:
            The Synse v3 API tags response.

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#tags
        """

        data = {
            'ns': ns,
            'ids': ids,
        }
        data = {k: v for k, v in data.items() if v is not None}

        r = await self.request('request/tags', data=data)
        return models.make_response(
            None,
            r['data'],
        )

    async def transaction(self, transaction_id: str) -> models.TransactionStatus:
        """Get the status of an asynchronous write transaction.

        Args:
            transaction_id (str): The ID of the transaction to get the status of.

        Returns:
            The Synse v3 API transaction response.

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#transaction
        """

        r = await self.request('request/transaction', data={
            'transaction': transaction_id,
        })
        return models.make_response(
            models.TransactionStatus,
            r['data'],
        )

    async def transactions(self) -> Iterable[str]:
        """Get a list of the transactions currently tracked by Synse.

        Returns:
            The Synse v3 API transactions response.

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#transactions
        """

        r = await self.request('request/transactions')
        return models.make_response(
            None,
            r['data'],
        )

    async def version(self) -> models.Version:
        """Get the version information for the configured Synse Server instance.

        Returns:
            The Synse v3 API version response.

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#version
        """

        r = await self.request('request/version')
        return models.make_response(
            models.Version,
            r['data'],
        )

    async def write_async(
            self, device: str, payload: Union[List[dict], dict],
    ) -> Iterable[models.TransactionInfo]:
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

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#write-asynchronous
        """

        data = {
            'device': device,
            'payload': payload,
        }
        data = {k: v for k, v in data.items() if v is not None}

        r = await self.request('request/write_async', data=data)
        return models.make_response(
            models.TransactionInfo,
            r['data'],
        )

    async def write_sync(
            self, device: str, payload: Union[List[dict], dict],
    ) -> Iterable[models.TransactionStatus]:
        """Write to the specified device synchronously.

        This method will wait until the write action has completed. It is up
        to the caller to ensure that a suitable timeout is set for the request.

        Args:
            device (str): The ID of the device to write to.
            payload (list[dict] | dict): The write payload.

        Returns:
            The Synse v3 API synchronous write response.

        See Also:
            https://synse.readthedocs.io/en/latest/server/api.v3/#write-synchronous
        """

        data = {
            'device': device,
            'payload': payload,
        }
        data = {k: v for k, v in data.items() if v is not None}

        r = await self.request('request/write_sync', data=data)
        return models.make_response(
            models.TransactionStatus,
            r['data'],
        )
