#!/usr/bin/env python
# coding: utf-8

import pytest
import pdc.util
import pandas as pd
from pdc.ptype import TypedFileName


def test_set_say_level():
    orig = pdc.util.SAY_LEVEL

    assert pdc.util.set_say_level() == orig
    assert pdc.util.set_say_level("error") == pdc.util.SAY_ERROR
    assert pdc.util.set_say_level(-1) == pdc.util.SAY_WARN
    assert pdc.util.set_say_level(-6) == pdc.util.SAY_TRACE
    assert pdc.util.set_say_level("debug") == pdc.util.SAY_DEBUG
    assert pdc.util.SAY_LEVEL == pdc.util.SAY_DEBUG
    assert pdc.util.set_say_level(orig) == orig


def test_saying_things(capfd):
    orig = pdc.util.SAY_LEVEL

    pdc.util.set_say_level("debug")
    pdc.util.say_debug("test name here")
    pdc.util.say_info("test name here")
    pdc.util.say_warn("test name here")
    pdc.util.say_error("test name here")
    _, err = capfd.readouterr()
    assert "[DEBUG] test name here\n" in err
    assert "[INFO] test name here\n" in err
    assert "[WARN] test name here\n" in err
    assert "[ERROR] test name here\n" in err

    pdc.util.set_say_level("error")
    pdc.util.say_debug("test name here")
    pdc.util.say_info("test name here")
    pdc.util.say_warn("test name here")
    pdc.util.say_error("test name here")
    _, err = capfd.readouterr()
    assert "[DEBUG] test name here\n" not in err
    assert "[INFO] test name here\n" not in err
    assert "[WARN] test name here\n" not in err
    assert "[ERROR] test name here\n" in err

    pdc.util.set_say_level(orig)


def test_df_compare_same():
    df1 = pd.DataFrame({"A": [1, 2], "B": [1, 2]})
    df2 = pd.DataFrame({"A": [1, 2], "B": [1, 2]})

    assert pdc.util.df_compare(df1, df2) is True


def test_df_compare_different_cell():
    df1 = pd.DataFrame({"A": [1, 2], "B": [1, 2]})
    df2 = pd.DataFrame({"A": [1, 2], "B": [1, 3]})

    assert pdc.util.df_compare(df1, df2) is False


def test_df_compare_different_len():
    df1 = pd.DataFrame({"A": [1, 2], "B": [1, 2]})
    df2 = pd.DataFrame({"A": [1, 2, 3], "B": [1, 2, 3]})

    assert pdc.util.df_compare(df1, df2) is False


def test_xlate_column_labels(ta_test1):
    assert pdc.util.xlate_column_labels(ta_test1.df, "var") == ["var"]
    assert pdc.util.xlate_column_labels(ta_test1.df, "val") == ["val"]
    assert pdc.util.xlate_column_labels(ta_test1.df, "var", "val") == ["val", "var"]

    assert pdc.util.xlate_column_labels(ta_test1.df, 1) == ["var"]
    assert pdc.util.xlate_column_labels(ta_test1.df, 2) == ["val"]

    assert pdc.util.xlate_column_labels(ta_test1.df, "v*") == ["val", "var"]
    assert pdc.util.xlate_column_labels(ta_test1.df, "v*l") == ["val"]


def test_compare_files(ta_test1, ta_test2):
    assert ta_test1 == ta_test1
    assert ta_test2 == ta_test2
    assert ta_test1 != ta_test2

    df = pd.concat([ta_test2.df] * 2, ignore_index=True)
    assert ta_test2 != df


def test_special_list_sort():
    i = pdc.util.special_list_sort("b")

    assert i("a") == "99a"
    assert i("b") == "00b"
    assert i("c") == "99c"


def test_json_with_headers_crashes(ta_test1):
    with pytest.raises(ValueError):
        pdc.util.read_file("test1.csv:t/asset/fmt_test1.json")


def test_unknown_format_crash():
    # grok_fname (aka TypedFileName.grok) won't let us specify an unknown
    # filetype, so we have to really force the issue to even test this
    # exception.
    tfn = TypedFileName("t/asset/test1.csv", "csv", "lol", None)

    with pytest.raises(ValueError):
        pdc.util.read_file(tfn)


def test_other_tsv_loader(ta_test_ofmt_fnamez):
    pnam, onam, ext = ta_test_ofmt_fnamez

    assert pnam.endswith(f".{ext}")
    assert onam.endswith(".csv")
    assert pnam[:-3] == pnam[:-3]

    pfil = pdc.util.read_file(pnam)
    ofil = pdc.util.read_file(onam)

    assert pfil == ofil
