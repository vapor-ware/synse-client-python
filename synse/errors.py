"""Errors and exceptions for the Synse API client."""

import json
import logging
from typing import Any

import aiohttp

log = logging.getLogger('synse')


class SynseError(Exception):
    """The base exception for all errors raised by the Synse API client."""


class InvalidInput(SynseError):
    """An error indicating that some user input to the API was invalid.

    HTTP Error Code: 400
    """


class NotFound(SynseError):
    """An error indicating that a specified resource was not found.

    HTTP Error Code: 404
    """


class ServerError(SynseError):
    """A general error indicating something went wrong during the
    server-side processing of the request.

    HTTP Error Code: 500
    """


# A mapping of HTTP status code to corresponding error class.
code_to_err = {
    400: InvalidInput,
    404: NotFound,
    500: ServerError,
}


async def wrap_and_raise_for_error(response: aiohttp.ClientResponse, body: Any = None) -> None:
    """Check if the response failed with a non-2XX status code.

    If the response has a non-2XX error code, wrap it in the appropriate
    client exception and re-raise. Otherwise, do nothing.

    Args:
        response: The response to check for a non-OK status.
        body: The data which provides context for the error. If this is
            not specified, the function will attempt to load it from
            response.text(), and fall back to response.reason. Note that this
            behavior is undesirable in some cases, such as for handling streamed
            responses, as calling response.text() will prevent the content from
            being loaded correctly. In such cases, a non-None body must be
            provided.

    Raises:
        SynseError: The response had a non-2XX error code.
    """

    if body is None:
        try:
            body = await response.text()
        except Exception as e:
            log.info('unable to get response text: {}'.format(e))
            body = response.reason

    try:
        response.raise_for_status()
    except aiohttp.ClientResponseError as e:
        log.error(f'request to {response.url} responded with {response.status}: {e}')
        error_cls = code_to_err.get(response.status)
        if error_cls is not None:
            try:
                data = json.loads(body)
            except Exception as e:
                log.error(f'failed to parse response JSON: {e}')
                raise error_cls(f'error: {body}') from e
            else:
                raise error_cls(data.get('context')) from e
        raise SynseError from e
