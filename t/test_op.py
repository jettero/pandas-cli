#!/usr/bin/env python
# coding: utf-8

import pytest
import pdc.op
from pdc.util import df_zipper


def test_concat_without_key(ta_test1, ta_test2, ta_t1Ct2):
    df = pdc.op.concat(ta_test1.df, ta_test2.df)
    for lhs, rhs in df_zipper(df, ta_t1Ct2.df):
        assert lhs == rhs


def test_concat_with_key(ta_test1, ta_test2, ta_t1Ct2Kvar):
    for k in ("var", ("var",), ["var"]):
        df = pdc.op.concat(ta_test1.df, ta_test2.df, key=k)
        for lhs, rhs in df_zipper(df, ta_t1Ct2Kvar):
            assert lhs == rhs

    with pytest.raises(ValueError):
        pdc.op.concat(ta_test1.df, ta_test2.df, key=(x for x in range(10)))


def test_transpocat_with_args(ta_test1, ta_test2, ta_t1TCt2Kvar):
    for k in ("var", ("var",), ["var"]):
        df = pdc.op.transpocat(ta_test1.df, ta_test2.df, key=k, merge_type="outer")
        for lhs, rhs in df_zipper(df, ta_t1TCt2Kvar.df):
            assert lhs == rhs

    with pytest.raises(ValueError):
        pdc.op.transpocat(ta_test1.df, ta_test2.df, key=(x for x in range(10)))


def test_transpocat_without_args(ta_test1, ta_test2, ta_t1TCt2):
    df = pdc.op.transpocat(ta_test1.df, ta_test2.df)
    for lhs, rhs in df_zipper(df, ta_t1TCt2.df):
        assert lhs == rhs


def test_filter_with_key(ta_test1, ta_test2):
    for k in ("var", ("var",), ["var"]):
        df = pdc.op.filter(ta_test1.df, ta_test2.df, key=k)
        ldf = len(df)
        lta = len(ta_test1.df)
        assert ldf == lta - 1

    with pytest.raises(ValueError):
        pdc.op.filter(ta_test1.df, ta_test2.df, key=(x for x in range(10)))


def test_filter_without_key(ta_test1, ta_test2):
    df = pdc.op.filter(ta_test1.df, ta_test2.df)
    ldf = len(df)
    lta = len(ta_test1.df)
    assert ldf == lta


def test_transpose(ta_test1):
    df = pdc.op.transpose(ta_test1.df)

    for i, thing in enumerate(zip(ta_test1.df["var"].tolist(), ta_test1.df["val"].tolist())):
        assert df[i].tolist() == list(thing)
