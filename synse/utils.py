"""Utilities for the Synse Python Client."""

from typing import List, Sequence, Tuple, Union

from multidict import MultiDict


def tag_params(
        tags: Union[None, str, Union[List[str], Tuple[str]], Sequence[Union[List[str], Tuple[str]]]],
        params: MultiDict,
) -> MultiDict:
    """Generate tag query parameters for a request.

    If no tags are specified, nothing is added to the query params MultiDict.

    Tags may be specified in a number of ways:
    - A single tag (single tag group)
    - A collection of tags (single tag group)
    - A collection of collections of tags (multiple tag groups)

    A single tag group is used to filter devices which match all of the
    tags in the group. If multiple tag groups are specified, the end result
    will be the set union of the results of the individual tag group filters.

    Args:
        tags: The tags to process into query parameters.
        params: The MultiDict which holds the query parameters for the request.

    Returns
        The 'params' MultiDict which was provided as a parameter.

    Raises:
        ValueError: The incoming tags are specified in an unsupported format.
    """

    if not tags:
        return params

    if isinstance(tags, str):
        params.add('tags', tags)
        return params

    elif isinstance(tags, Sequence):
        if len(tags) == 0:
            return params

        if isinstance(tags[0], (List, Tuple)):
            for group in tags:
                params.add('tags', ','.join(group))
            return params

        elif isinstance(tags[0], str):
            params.add('tags', ','.join(tags))
            return params

    raise ValueError(
        f'Unable to process tag params: tags must be either str, Sequence[str], '
        f'or Sequence[Sequence[str]], but was {type(tags)}'
    )
