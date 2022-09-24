#!/usr/bin/env python
# coding: utf-8


def test_csv(csv1_mb):
    r1 = csv1_mb.read(128)  # h
    h = csv1_mb.head()  # h
    r2 = csv1_mb.read(128)  # h
    r3 = csv1_mb.read(128)  # !h
    csv1_mb.reset()
    r4 = csv1_mb.read(128)  # h

    assert r1 == h
    assert r2 == r1
    assert r2 != r3
    assert r1 == r4
