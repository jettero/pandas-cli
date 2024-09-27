#!/usr/bin/env python
# coding: utf-8

import pytest
from pdc.util import read_csv


def test_reading_cached_files_cache_not_ok(ta_test):
    df = read_csv(ta_test.fname, cache_ok=False)
    assert df.fname == ta_test.fname
    assert df == ta_test
    assert df is not ta_test


def test_reading_cached_files_cache_ok(ta_test):
    df = read_csv(ta_test.fname, cache_ok=True)
    assert df.fname == ta_test.fname
    assert df == ta_test
    assert df is ta_test


@pytest.mark.parametrize("sh_by_name", ["", "sh_by_name"])
@pytest.mark.parametrize("via_setter", ["", "via_setter"])
@pytest.mark.parametrize("add_file", ["", "add_file"])
def test_file_cache_set_headers(FILE_CACHE, ta_test, add_file, via_setter, sh_by_name):
    # We're testing various cache mechanisms, so we first bottom out the cache
    # regards to anything that might already be in there (*ahem* ta_test should
    # be in there already).
    FILE_CACHE.clear()

    assert FILE_CACHE.HEADERS_FROM is None
    assert FILE_CACHE.headers_from is None

    if add_file or sh_by_name:
        FILE_CACHE.add_file(ta_test)
        assert FILE_CACHE.HEADERS_FROM is None
        assert FILE_CACHE.headers_from is ta_test
    else:
        assert FILE_CACHE.HEADERS_FROM is None
        assert FILE_CACHE.headers_from is None

    if via_setter:
        FILE_CACHE.headers_from = ta_test.fname if sh_by_name else ta_test
    else:
        FILE_CACHE.set_headers_from(ta_test.fname if sh_by_name else ta_test)

    assert FILE_CACHE.HEADERS_FROM == ta_test.fname
    assert FILE_CACHE.headers_from is ta_test

    if via_setter:
        FILE_CACHE.headers_from = False
    else:
        FILE_CACHE.set_headers_from(False)

    assert FILE_CACHE.HEADERS_FROM is None
    assert FILE_CACHE.headers_from is ta_test

    with pytest.raises(KeyError):
        if via_setter:
            FILE_CACHE.headers_from = "/etc/passwd"
        else:
            FILE_CACHE.set_headers_from("/etc/passwd")
