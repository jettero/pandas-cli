#!/usr/bin/env python
# coding: utf-8

import sys
import subprocess
from io import UnsupportedOperation

import pytest

from pandas_cli.magic_buffer import MagicBuffer


@pytest.fixture
def pretend_stdin(csv1):
    p = subprocess.Popen(["cat", csv1], stdout=subprocess.PIPE)
    yield p.stdout
    p.wait()


@pytest.fixture
def ps_mb(pretend_stdin):
    yield MagicBuffer(pretend_stdin)


def _std_test_mb(mb):
    r1 = mb.read(128)  # h
    h = mb.head()  # h
    r2 = mb.read(128)  # h
    r3 = mb.read(128)  # !h
    mb.reset()
    r4 = mb.read(128)  # h

    assert r1 == h
    assert r2 == r1
    assert r2 != r3
    assert r1 == r4


def test_csv(csv1_mb):
    _std_test_mb(csv1_mb)


def test_pretend_stdin(pretend_stdin):
    with pytest.raises(UnsupportedOperation) as excinfo:
        pretend_stdin.seek(0)


def test_ps_mb(ps_mb):
    _std_test_mb(ps_mb)
