#!/usr/bin/env python
# coding: utf-8

import os
import pytest

import pdc.util

from t.bin.gen_csv import main as gen_csv
from t.bin.gen_json import main as gen_json


@pytest.fixture
def csv1(filename="t/output/1.csv"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    gen_csv("--output-file", filename)
    yield filename


@pytest.fixture
def json1(filename="t/output/1.json"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    gen_csv("--output-file", filename)
    yield filename


def _fh(fname):
    fh = open(fname, "r")
    yield fh
    fh.close()


@pytest.fixture
def csv1_fh(csv1):
    yield from _fh(csv1)


@pytest.fixture
def json1_fh(json1):
    yield from _fh(json1)


@pytest.fixture(scope="module")
def f1():
    yield pdc.util.read_csv("t/asset/test1.csv", id=1)


@pytest.fixture(scope="module")
def f2():
    yield pdc.util.read_csv("t/asset/test2.csv", id=2)


@pytest.fixture(scope="module")
def f3():
    yield pdc.util.read_csv("t/asset/test3.csv", id=3)
