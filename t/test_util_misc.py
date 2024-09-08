#!/usr/bin/env python
# coding: utf-8

import pdc.util


def test_set_say_level():
    orig = pdc.util.SAY_LEVEL

    assert pdc.util.set_say_level() == orig
    assert pdc.util.set_say_level("debug") == pdc.util.SAY_DEBUG
    assert pdc.util.SAY_LEVEL == pdc.util.SAY_DEBUG
    assert pdc.util.set_say_level(orig) == orig
