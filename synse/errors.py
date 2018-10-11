"""Errors and exceptions for the Synse API client."""


# TODO (etd) - tie in the responses.Error with this. if the error is a 400, 404, or
# 500 from Synse Server, we should generally have some JSON with it.

class SynseError(Exception):
    """The base exception for all errors raised by the Synse API client."""


class InvalidInput(SynseError):
    """

    Error Code: 400
    """


class NotFound(SynseError):
    """

    Error Code: 404
    """


class ServerError(SynseError):
    """

    Error Code: 500
    """
