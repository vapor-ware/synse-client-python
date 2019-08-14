"""Tests for the synse.errors package."""

import pytest

from synse import errors


@pytest.mark.asyncio
async def test_wrap_and_raise_for_error_no_error(client_response) -> None:

    client_response.status = 200

    try:
        await errors.wrap_and_raise_for_error(client_response)
    except Exception as e:
        pytest.fail(f'unexpected exception: {e}')


@pytest.mark.asyncio
async def test_wrap_and_raise_for_error_no_json_body(client_response) -> None:

    client_response.status = 404
    client_response.reason = "not found"
    client_response.content = None

    with pytest.raises(errors.NotFound):
        await errors.wrap_and_raise_for_error(client_response)


@pytest.mark.asyncio
async def test_wrap_and_raise_for_error_400(loop, client_response) -> None:

    def side_effect(*args, **kwargs):
        fut = loop.create_future()
        fut.set_result(b'{"context":"test"}')
        return fut

    client_response.status = 400
    client_response.reason = 'testing'
    client_response.content.read.side_effect = side_effect

    with pytest.raises(errors.InvalidInput):
        await errors.wrap_and_raise_for_error(client_response)


@pytest.mark.asyncio
async def test_wrap_and_raise_for_error_404(loop, client_response) -> None:

    def side_effect(*args, **kwargs):
        fut = loop.create_future()
        fut.set_result(b'{"context":"test"}')
        return fut

    client_response.status = 404
    client_response.reason = 'testing'
    client_response.content.read.side_effect = side_effect

    with pytest.raises(errors.NotFound):
        await errors.wrap_and_raise_for_error(client_response)


@pytest.mark.asyncio
async def test_wrap_and_raise_for_error_500(loop, client_response) -> None:

    def side_effect(*args, **kwargs):
        fut = loop.create_future()
        fut.set_result(b'{"context":"test"}')
        return fut

    client_response.status = 500
    client_response.reason = 'testing'
    client_response.content.read.side_effect = side_effect

    with pytest.raises(errors.ServerError):
        await errors.wrap_and_raise_for_error(client_response)


@pytest.mark.asyncio
async def test_wrap_and_raise_for_error_general(client_response) -> None:

    client_response.status = 403
    client_response.reason = 'testing'

    with pytest.raises(errors.SynseError):
        await errors.wrap_and_raise_for_error(client_response)
