#!/usr/bin/env python
# coding: utf-8

import pytest
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
