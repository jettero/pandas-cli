#!/usr/bin/env python
# coding: utf-8

import pytest
import pdc.op
import pdc.parser
from pdc.util import df_zipper
from pdc.parser import Call, Idx, transformer


@pytest.fixture
def listoid():
    yield list(range(17, 17 + 20, 2))


def test_idx(listoid):
    i = Idx(1, 0, "listoid", listoid)
    assert i.op == 1
    assert i.idx == 0
    assert i.snam == "listoid"
    assert i.src is listoid
    assert i.deref == 17
    assert i.short == "{l1}"
    assert i() == i.deref

    j = Idx(1000, 999, "listoid", listoid)
    with pytest.raises(IndexError):
        j.deref

    assert j() == None


def test_op_idx_missed_items(listoid):
    # This is missed in the actual parser test because src= is always specified
    # but I wanted to leave the None=>tmpvz implication if block.
    i = transformer.op_idx("0")
    assert i.src is transformer.tmpvz

    j = transformer.op_idx("2", listoid)
    assert j.short == "{?2}"
    assert j.deref == 19


def test_concat(ta_test1, ta_test2, ta_t1Ct2):
    pf = pdc.parser.parse("f1+f2", files=(ta_test1, ta_test2))

    assert pf.fn is pdc.op.concat
    assert pf.args[0].deref is ta_test1
    assert pf.args[1].deref is ta_test2

    df = pf()

    ldf = len(df)
    lta = len(ta_t1Ct2)
    assert ldf == lta

    for lhs, rhs in df_zipper(df, ta_t1Ct2.df):
        assert lhs == rhs


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


# def test_concat_nested_kwargs(ta_test1, ta_test2, ta_test3, ta_t1Ct2KvarCt3):
#     pf = pdc.parser.parse("f1 + f2 @ var; t1 + f3", files=(ta_test1, ta_test2, ta_test3))  # parsed frame

#     assert pf.args[1].deref is ta_test3
#     assert pf.kw == dict()

#     ipf = pf.args[0].deref  # inner parsed frame
#     assert ipf.args[0].deref is ta_test1
#     assert ipf.args[1].deref is ta_test2
#     assert ipf.kw == dict(key=set(["var"]))

#     df = pf()

#     ldf = len(df)
#     lta = len(ta_t1Ct2KvarCt3)
#     assert ldf == lta

#     for lhs, rhs in df_zipper(df, ta_t1Ct2KvarCt3.df):
#         assert lhs == rhs


# def test_invalid_file_fail():
#     with pytest.raises(ValueError):
#         pdc.parser.parse("f1 + f2", files=(3, 4, 5))
