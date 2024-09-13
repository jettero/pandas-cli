#!/usr/bin/env python
# coding: utf-8

import os
import pytest
from glob import glob

import pdc.util

from t.bin.gen_csv import main as gen_csv
from t.bin.gen_json import main as gen_json

TA_TEST = glob("t/asset/test*.csv")


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


@pytest.fixture(scope="module", params=TA_TEST)
def ta_test_fname(request):
    yield request.param


@pytest.fixture(scope="module")
def ta_test(ta_test_fname):
    yield pdc.util.read_csv(ta_test_fname)


@pytest.fixture(scope="module")
def ta_test_all():
    yield tuple(pdc.util.read_csv(x) for x in TA_TEST)


for i, path in enumerate(TA_TEST, start=1):

    def fixture_func(file=path):
        @pytest.fixture(scope="module")
        def _fixture():
            return pdc.util.read_csv(file)

        return _fixture

    fname = os.path.basename(path).split(".")[0]
    fixture_func.__name__ = fname
    globals()[f"ta_{fname}"] = fixture_func()
