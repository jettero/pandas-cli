#!/usr/bin/env python
# coding: utf-8

import pytest
from pdc.fname_parser import grok_fname


def test_basic():
    assert grok_fname("t/asset/test1.csv").fname == "t/asset/test1.csv"


def test_hf_rel_name():
    t1nh = grok_fname("t/asset/test1.csv:t/asset/test1_nh.csv")
    assert t1nh.fname == "t/asset/test1_nh.csv"
    assert t1nh.hsrc.fname == "t/asset/test1.csv"


def test_hf_short_name():
    t1nh = grok_fname("test1.csv:t/asset/test1_nh.csv")
    assert t1nh.fname == "t/asset/test1_nh.csv"
    assert t1nh.hsrc.fname == "test1.csv"


def test_hf_last_fail():
    with pytest.raises(KeyError):
        grok_fname(":t/asset/test1_nh.csv")


# NOTE: t/conftest.py clears the FILE_CACHE before each test function so
# for the below colon-leader tests to not fail, we have to load something into
# grok_fname(last_file=).


def test_hf_last_fail():
    with pytest.raises(KeyError):
        grok_fname(":t/asset/test1_nh.csv")


def test_hf_last_by_TypedFileName():
    t1wh = grok_fname("t/asset/test1.csv")
    t1nh = grok_fname(":t/asset/test1_nh.csv", last_file=t1wh)
    assert t1nh.fname == "t/asset/test1_nh.csv"
    assert t1nh.hsrc is t1wh


def test_hf_last_by_File(ta_test1):
    t1nh = grok_fname(":t/asset/test1_nh.csv", last_file=ta_test1)
    assert t1nh.fname == "t/asset/test1_nh.csv"
    assert t1nh.hsrc.fname == ta_test1.fname


def test_hf_last_by_str(ta_test1):
    t1nh = grok_fname(":t/asset/test1_nh.csv", last_file="t/asset/test1.csv")
    assert t1nh.fname == "t/asset/test1_nh.csv"
    assert t1nh.hsrc.fname == "t/asset/test1.csv"


def test_hf_various_file_extensions():
    assert grok_fname("t/asset/test1.csv").ftype == "csv"
    assert grok_fname("t/asset/test1.tsv").ftype == "tsv"

    assert grok_fname("t/asset/fmt_test1.xlsx").ftype == "excel"

    assert grok_fname("t/asset/fmt_test1.xls@excel").ftype == "excel"
    assert grok_fname("t/asset/fmt_test1.xlsx@excel").ftype == "excel"
    assert grok_fname("t/asset/fmt_test1.xlsx@xls").ftype == "excel"
    assert grok_fname("t/asset/fmt_test1.xlsx@xlsx").ftype == "excel"
