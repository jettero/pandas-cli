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


def test_transpocat(ta_test1, ta_test2, ta_t1TCt2Kvar):
    pf = pdc.parser.parse("f1 . f2 @ var", files=(ta_test1, ta_test2))

    assert pf.fn is pdc.op.transpocat
    assert pf.args[0].deref is ta_test1
    assert pf.args[1].deref is ta_test2

    df = pf()
    assert ta_t1TCt2Kvar == df


def test_transpose(ta_test1, ta_t1transposed):
    pf = pdc.parser.parse("f1^", files=(ta_test1,))

    assert pf.fn is pdc.op.transpose
    assert pf.args[0].deref is ta_test1

    # NOTE: when we read in a csv, the types of columns are inferred by pandas.
    # but when the columns are transposed to rows, the integer column of test1
    # becomes an integer row, and then pandas infers a string type on each
    # column.  to make the below work out, we have to first convert
    # ta_test1.df['val'] to strings.

    ta_test1.df["val"] = ta_test1.df["val"].map(str)

    df = pf()
    assert df.flags.get("transposed") is True
    assert ta_t1transposed == df


def test_reduce_t1Ct2(ta_test1, ta_test2, ta_t1Ct2):
    pf = pdc.parser.parse("f*: a + b", files=(ta_test1, ta_test2))

    assert pf.fn is pdc.op.concat
    assert pf.args[0].deref is ta_test1
    assert pf.args[1].deref is ta_test2

    df = pf()
    assert ta_t1Ct2 == df


def test_reduce_t1Ct2Ct3(ta_test1, ta_test2, ta_test3, ta_t1Ct2, ta_t1Ct2Ct3):
    filez = (ta_test1, ta_test2, ta_test3)

    pf = pdc.parser.parse("f/test[12].csv/: a + b", files=filez)

    assert pf.fn is pdc.op.concat
    assert pf.args[0].deref is ta_test1
    assert pf.args[1].deref is ta_test2

    df = pf()
    assert ta_t1Ct2 == df

    pf = pdc.parser.parse("f(t/asset/test*.csv): a + b", files=filez)

    assert pf.fn is pdc.op.concat
    assert pf.args[0].args[0].deref is ta_test1
    assert pf.args[0].args[1].deref is ta_test2
    assert pf.args[1].deref is ta_test3

    df = pf()
    assert ta_t1Ct2Ct3 == df


def test_reduce_tmp_wild(ta_test1, ta_test2, ta_test3):
    pf = pdc.parser.parse("f1+f2;f3; t*: a+b", files=(ta_test1, ta_test2, ta_test3))

    assert pf.fn is pdc.op.concat
    assert pf.args[0].deref.args[0].deref is ta_test1
    assert pf.args[0].deref.args[1].deref is ta_test2
    assert pf.args[1].deref is ta_test3
