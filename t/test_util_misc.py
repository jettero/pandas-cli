#!/usr/bin/env python
# coding: utf-8

import pytest
import pdc.util
import pandas as pd
from .conftest import TA_TEST


def test_set_say_level():
    orig = pdc.util.SAY_LEVEL

    assert pdc.util.set_say_level() == orig
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


def test_read_csv_header_modalities(ta_test_fname):
    # NOTE: this is wrong... each of these t/asset/test*.csv files has headers.
    f1 = pdc.util.read_csv(ta_test_fname)
    fz = (
        pdc.util.read_csv(ta_test_fname, headers=f1),
        pdc.util.read_csv(ta_test_fname, headers=f1.df),
        pdc.util.read_csv(ta_test_fname, headers=f1.columns),
        pdc.util.read_csv(ta_test_fname, headers=True),
        pdc.util.read_csv(ta_test_fname, headers=False),
        pdc.util.read_csv(ta_test_fname, headers=None),
    )

    for f in fz:
        assert isinstance(f, pdc.util.File)
        assert f1.columns == f.columns

    for c in f1.columns:
        # NOTE: by specifying the headers above, we pretend the files don't
        # have headers -- but they do, so we have to skip the header in the RHS
        # below

        # NOTE: also, when a numeric column begins with a string (the header),
        # pandas assumes the whole column is strings; which is reasonable, so
        # we hvae to convert the LHS to strings in order to match.

        def convert(*x):
            return [str(y).lower() for y in x]

        lhs = convert(*(str(x) for x in f1.df[c].tolist()))
        for f in fz:
            assert lhs == convert(*f.df[c].tolist()[(1 if f.flags.get("derived_headers") else 0) :])


def test_read_csv_header_fail_modalities(ta_test_fname):
    for item in ((x for x in "supz"), "supz", 7):
        with pytest.raises(ValueError):
            pdc.util.read_csv(ta_test_fname, headers=item)


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
