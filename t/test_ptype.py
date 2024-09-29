#!/usr/bin/env python
# coding: utf-8

import pytest
from pdc.ptype import Idx
from pdc.parser import transformer


@pytest.fixture
def listoid():
    yield list(range(17, 17 + 20, 2))


def test_idx(listoid):
    i = Idx(1, 0, "l?", listoid)
    assert i.op == 1
    assert i.idx == 0
    assert i.snam == "l?"
    assert i.src is listoid
    assert i.deref == 17
    assert i.short == "{l1}"
    assert i() == i.deref

    j = Idx(1000, 999, "l?", listoid)
    with pytest.raises(IndexError):
        j.deref

    assert j() == None


def test_op_idx_missed_items(listoid):
    # The parser always specifies src=<something>.
    # but it's worth testing what happens if you
    # omit the kwarg
    i = transformer.op_idx("0")
    assert i.src is transformer.tmpvz

    j = transformer.op_idx("2", listoid)
    assert j.short == "{??2}"
    assert j.deref == 19


def test_op_idx_sv_items():
    lhs = transformer.op_idx("1", src=transformer.sv)
    assert lhs.snam == "lhs"

    rhs = transformer.op_idx("2", src=transformer.sv)
    assert rhs.snam == "rhs"

    lol = transformer.op_idx("3", src=transformer.sv)
    assert lol.snam == "sv?"
