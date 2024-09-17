#!/usr/bin/env python
# coding: utf-8

import pytest
import pdc.op

def df_zipper(*df):
    yield from zip(*(sorted(x.to_records(index=False).tolist()) for x in df))

def test_concat_without_key(ta_test1, ta_test2, ta_t1Ct2):
    df = pdc.op.concat(ta_test1.df, ta_test2.df)
    for lhs, rhs in df_zipper(df, ta_t1Ct2.df):
        assert lhs == rhs

def test_concat_with_key(ta_test1, ta_test2, ta_t1Ct2Kvar):
    for k in ("var", ("var",), ["var"]):
        df = pdc.op.concat(ta_test1.df, ta_test2.df, key=k)
        for lhs, rhs in df_zipper(df, ta_t1Ct2Kvar.df):
            assert lhs == rhs

    with pytest.raises(ValueError):
        pdc.op.concat(ta_test1.df, ta_test2.df, key=(x for x in range(10)))

def test_transpocat_with_args(ta_test1, ta_test2, ta_t1TCt2Kvar):
    for k in ("var", ("var",), ["var"]):
        df = pdc.op.transpocat(ta_test1.df, ta_test2.df, key=k, merge_type="outer")
        for lhs, rhs in df_zipper(df, ta_t1TCt2Kvar.df):
            assert lhs == rhs

def test_transpocat_without_args(ta_test1, ta_test2, ta_t1TCt2):
    df = pdc.op.transpocat(ta_test1.df, ta_test2.df)
    for lhs, rhs in df_zipper(df, ta_t1TCt2.df):
        assert lhs == rhs


def test_filter(ta_test1, ta_test2):
    df = pdc.op.filter(ta_test1.df, ta_test2.df, key="var")
    ldf = len(df)
    lta = len(ta_test1.df)

    assert ldf == lta - 1
