
import pytest
from requests import Response

from synse import errors


def test_wrap_and_raise_for_error_no_error():

    r = Response()
    r.status_code = 200

    try:
        errors.wrap_and_raise_for_error(r)
    except Exception as e:
        pytest.fail(f'unexpected exception: {e}')


def test_wrap_and_raise_for_error_400():

    r = Response()
    r.status_code = 400
    r._content = b'{"context":"test"}'

    with pytest.raises(errors.InvalidInput):
        errors.wrap_and_raise_for_error(r)


def test_wrap_and_raise_for_error_404():
    r = Response()
    r.status_code = 404
    r._content = b'{"context":"test"}'

    with pytest.raises(errors.NotFound):
        errors.wrap_and_raise_for_error(r)


def test_wrap_and_raise_for_error_500():
    r = Response()
    r.status_code = 500
    r._content = b'{"context":"test"}'

    with pytest.raises(errors.ServerError):
        errors.wrap_and_raise_for_error(r)


def test_wrap_and_raise_for_error_general():
    r = Response()
    r.status_code = 403

    with pytest.raises(errors.SynseError):
        errors.wrap_and_raise_for_error(r)
