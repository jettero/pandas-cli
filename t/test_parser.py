#!/usr/bin/env python
# coding: utf-8

import pdc.op
import pdc.parser


def test_simple_concat(f1, f2):
    t = pdc.parser.parse("f1+f2", files=(f1, f2))

    assert t.fn is pdc.op.concat
    assert t.args[0] is f1
    assert t.args[1] is f2

    c = t()

    assert len(f1.df) + len(f2.df) == len(c)
