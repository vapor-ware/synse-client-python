"""Errors and exceptions for the Synse API client."""

import logging

import requests

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


def wrap_and_raise_for_error(response: requests.Response) -> None:
    """Check if the response failed with a non-2XX status code.

    If the response has a non-2XX error code, wrap it in the appropriate
    client exception and re-raise. Otherwise, do nothing.

    Args:
        response (requests.Response): The response to check for a
            non-OK status.

    Raises:
        SynseError: The response had a non-2XX error code.
    """
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        log.error(f'request to {response.url} responded with {response.status_code}: {e}')
        error_cls = code_to_err.get(response.status_code)
        if error_cls is not None:
            try:
                data = response.json()
            except Exception as e:
                log.error(f'failed to parse response JSON: {e}')
                raise error_cls from e
            else:
                raise error_cls(data.get('context')) from e
        raise SynseError from e
