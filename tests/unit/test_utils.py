"""Tests for the synse.utils package."""

import aiohttp
import pytest
from multidict import MultiDict

from synse import errors, utils


@pytest.mark.parametrize(
    'tags,expected', [
        # Empty tags
        (None, {}),
        ('', {}),
        ([], {}),

        # Single tag
        ('foo', {'tags': 'foo'}),
        ('foo/bar', {'tags': 'foo/bar'}),
        ('foo/test:bar', {'tags': 'foo/test:bar'}),

        # Single tag group
        (['foo1'], {'tags': 'foo1'}),
        (('foo1',), {'tags': 'foo1'}),
        (['foo1', 'foo2'], {'tags': 'foo1,foo2'}),
        (['foo1/bar', 'foo2/test:baz'], {'tags': 'foo1/bar,foo2/test:baz'}),

        # Multiple tag groups
        ([['foo'], ['bar']], MultiDict([('tags', 'foo'), ('tags', 'bar')])),
        ((['foo'], ['bar']), MultiDict([('tags', 'foo'), ('tags', 'bar')])),
        ((('foo',), ('bar',)), MultiDict([('tags', 'foo'), ('tags', 'bar')])),
        ([['foo', 'abc'], ['bar']], MultiDict([('tags', 'foo,abc'), ('tags', 'bar')])),
        ([['foo/bar', 'abc/test:123'], ['bar/test:baz']], MultiDict([('tags', 'foo/bar,abc/test:123'), ('tags', 'bar/test:baz')])),
    ]
)
def test_tag_params(tags, expected):

    results = utils.tag_params(tags, MultiDict())
    assert results == expected


def test_tag_params_error():

    with pytest.raises(ValueError):
        utils.tag_params({'foo': 'bar/baz'}, MultiDict())


def test_process_ws_response_ok_dict():
    message = aiohttp.WSMessage(
        aiohttp.WSMsgType.text,
        '{"id":1,"event":"response/test","data":{"foo": "bar"}}',
        None,
    )

    resp = utils.process_ws_response(message)
    assert resp == {'id': 1, 'event': 'response/test', 'data': {'foo': 'bar'}}


def test_process_ws_response_ok_list():
    message = aiohttp.WSMessage(
        aiohttp.WSMsgType.text,
        '{"id":1,"event":"response/test","data":[1, 2, 3]}',
        None,
    )

    resp = utils.process_ws_response(message)
    assert resp == {'id': 1, 'event': 'response/test', 'data': [1, 2, 3]}


def test_process_ws_response_error_500():
    message = aiohttp.WSMessage(
        aiohttp.WSMsgType.text,
        '{"id":-1,"event":"response/error","data":{"http_code": 500, "description": "foo"}}',
        None,
    )

    with pytest.raises(errors.SynseError):
        utils.process_ws_response(message)


def test_process_ws_response_error_404():
    message = aiohttp.WSMessage(
        aiohttp.WSMsgType.text,
        '{"id":-1,"event":"response/error","data":{"http_code": 404, "description": "foo"}}',
        None,
    )

    with pytest.raises(errors.NotFound):
        utils.process_ws_response(message)


def test_process_ws_response_error_400():
    message = aiohttp.WSMessage(
        aiohttp.WSMsgType.text,
        '{"id":-1,"event":"response/error","data":{"http_code": 400, "description": "foo"}}',
        None,
    )

    with pytest.raises(errors.InvalidInput):
        utils.process_ws_response(message)


def test_process_ws_response_error_closed():
    message = aiohttp.WSMessage(
        aiohttp.WSMsgType.closed,
        None,
        None,
    )

    with pytest.raises(errors.SynseError):
        utils.process_ws_response(message)


def test_process_ws_response_error_error():
    message = aiohttp.WSMessage(
        aiohttp.WSMsgType.error,
        None,
        None,
    )

    with pytest.raises(errors.SynseError):
        utils.process_ws_response(message)


def test_process_ws_response_error_unknown():
    message = aiohttp.WSMessage(
        aiohttp.WSMsgType.binary,
        None,
        None,
    )

    with pytest.raises(errors.SynseError):
        utils.process_ws_response(message)
