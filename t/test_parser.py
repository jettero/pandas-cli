#!/usr/bin/env python
# coding: utf-8

import pytest
import pdc.op
import pdc.parser
from pdc.util import df_zipper


def test_invalid_file_fail():
    with pytest.raises(ValueError):
        pdc.parser.parse("f1 + f2", files=(3, 4, 5))


def test_concat(ta_test1, ta_test2, ta_t1Ct2):
    pf = pdc.parser.parse("f1+f2", files=(ta_test1, ta_test2))

    assert pf.fn is pdc.op.concat
    assert pf.args[0].deref is ta_test1
    assert pf.args[1].deref is ta_test2

    df = pf()
    assert ta_t1Ct2 == df


def test_concat_kwargs(ta_test1, ta_test2, ta_t1Ct2Kvar):
    pf = pdc.parser.parse("f1 + f2 @ var", files=(ta_test1, ta_test2))
    assert pf.args[0].deref is ta_test1
    assert pf.args[1].deref is ta_test2
    assert pf.kw == dict(key=set(["var"]))

    df = pf()

    ldf = len(df)
    lta = len(ta_t1Ct2Kvar)
    assert ldf == lta

    for lhs, rhs in df_zipper(df, ta_t1Ct2Kvar.df):
        assert lhs == rhs


def test_concat_nested_kwargs(ta_test1, ta_test2, ta_test3, ta_t1Ct2Kvar, ta_t1Ct2KvarCt3):
    pf = pdc.parser.parse("f1 + f2 @ var; t1 + f3", files=(ta_test1, ta_test2, ta_test3))

    assert pf.args[1].deref is ta_test3
    assert pf.kw == dict()

    ipf = pf.args[0].deref  # inner parsed frame
    assert ipf.args[0].deref is ta_test1
    assert ipf.args[1].deref is ta_test2
    assert ipf.kw == dict(key=set(["var"]))

    ##########################
    t1 = pf.args[0]()

    lt1 = len(t1)
    lta = len(ta_t1Ct2Kvar)
    assert lt1 == lta

    for lhs, rhs in df_zipper(t1, ta_t1Ct2Kvar.df):
        assert lhs == rhs

    ##########################
    df = pf()

    ldf = len(df)
    lta = len(ta_t1Ct2KvarCt3)
    assert ldf == lta

    for lhs, rhs in df_zipper(df, ta_t1Ct2KvarCt3.df):
        assert lhs == rhs


def test_filter(ta_test1, ta_test2, ta_t1Ft2):
    pf = pdc.parser.parse("f1-f2", files=(ta_test1, ta_test2))

    assert pf.fn is pdc.op.filter
    assert pf.args[0].deref is ta_test1
    assert pf.args[1].deref is ta_test2

    df = pf()

    ldf = len(df)
    lta = len(ta_t1Ft2)
    assert ldf == lta

    for lhs, rhs in df_zipper(df, ta_t1Ft2.df):
        assert lhs == rhs


def test_filter(ta_test1, ta_test2, ta_t1Ft2Kvar):
    pf = pdc.parser.parse("f1 - f2 @ var", files=(ta_test1, ta_test2))

    assert pf.fn is pdc.op.filter
    assert pf.args[0].deref is ta_test1
    assert pf.args[1].deref is ta_test2

    df = pf()

    ldf = len(df)
    lta = len(ta_t1Ft2Kvar)
    assert ldf == lta

    for lhs, rhs in df_zipper(df, ta_t1Ft2Kvar.df):
        assert lhs == rhs


@pytest.mark.xfail
def test_reduce(ta_test1, ta_test2, ta_t1Ct2):
    pf = pdc.parser.parse("f*: a + b", files=(ta_test1, ta_test2))

    # assert pf.fn is pdc.op.concat
    # assert pf.args[0].deref is ta_test1
    # assert pf.args[1].deref is ta_test2

    df = pf()
    assert ta_t1Ct2 == df
