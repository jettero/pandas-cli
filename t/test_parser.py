#!/usr/bin/env python
# coding: utf-8

import pdc.op
import pdc.parser


def test_simple_concat(f1, f2):
    pf = pdc.parser.parse("f1+f2", files=(f1, f2))

    assert pf.fn is pdc.op.concat
    assert pf.args[0]() is f1
    assert pf.args[1]() is f2

    df = pf()

    assert len(f1.df) + len(f2.df) == len(df)


def test_kwargs(f1, f2):
    pf = pdc.parser.parse("f1 + f2 @ var", files=(f1, f2))
    assert pf.args[0] is f1
    assert pf.args[1] is f2
    assert pf.kw == dict(key="var")


def test_kwargs(f1, f2, f3):
    pf = pdc.parser.parse("f1 + f2 @ var; t1 + f3", files=(f1, f2, f3))  # parsed frame

    assert pf.args[1].deref is f3
    assert pf.kw == dict()

    ipf = pf.args[0].deref  # inner parsed frame
    assert ipf.args[0].deref is f1
    assert ipf.args[1].deref is f2
    assert ipf.kw == dict(key=set(["var"]))
