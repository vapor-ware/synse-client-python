"""Tests for the synse.utils package."""

import pytest
from multidict import MultiDict

from synse import utils


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
