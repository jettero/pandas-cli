#!/usr/bin/env python
# coding: utf-8

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
