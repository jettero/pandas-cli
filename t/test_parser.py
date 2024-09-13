#!/usr/bin/env python
# coding: utf-8

import pdc.op
import pdc.parser


def test_simple_concat(ta_test1, ta_test2):
    pf = pdc.parser.parse("f1+f2", files=(ta_test1, ta_test2))

    assert pf.fn is pdc.op.concat
    assert pf.args[0]() is ta_test1
    assert pf.args[1]() is ta_test2

    df = pf()

    assert len(ta_test1) + len(ta_test2) == len(df)


def test_kwargs(ta_test1, ta_test2):
    pf = pdc.parser.parse("f1 + f2 @ var", files=(ta_test1, ta_test2))
    assert pf.args[0] is ta_test1
    assert pf.args[1] is ta_test2
    assert pf.kw == dict(key="var")


def test_kwargs(ta_test1, ta_test2, ta_test3):
    pf = pdc.parser.parse("f1 + f2 @ var; t1 + f3", files=(ta_test1, ta_test2, ta_test3))  # parsed frame

    assert pf.args[1].deref is ta_test3
    assert pf.kw == dict()

    ipf = pf.args[0].deref  # inner parsed frame
    assert ipf.args[0].deref is ta_test1
    assert ipf.args[1].deref is ta_test2
    assert ipf.kw == dict(key=set(["var"]))

    df = pf()

    duplicate_var_count = 1

    assert len(ta_test1) + len(ta_test2) + len(ta_test3) == len(df) + duplicate_var_count
