#!/usr/bin/env python
# coding: utf-8

from pdc.util import special_list_sort as sls


def test_items1():
    i = sls("b")

    assert i("a") == "99a"
    assert i("b") == "00b"
    assert i("c") == "99c"
