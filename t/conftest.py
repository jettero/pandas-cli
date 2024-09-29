#!/usr/bin/env python
# coding: utf-8

import os
import pytest
from glob import glob

import pdc.util

TA_NHT = set(glob("t/asset/*_nh.csv"))
TA_TEST = set(glob("t/asset/test*.csv")) - TA_NHT
TA_OTHER = set(glob("t/asset/*.csv")) - set(TA_TEST).union(TA_NHT)

TA_NHT = tuple(sorted(TA_NHT))
TA_TEST = tuple(sorted(TA_TEST))
TA_OTHER = tuple(sorted(TA_OTHER))

__all__ = ["TA_TEST", "TA_OTHER"]


@pytest.fixture(autouse=True)
def FILE_CACHE():
    # any fixtures that should be cached, must include FILE_CACHE as a
    # dependency, or the cache will seem to be missing the fixture in question.
    pdc.util.FILE_CACHE.clear()
    yield pdc.util.FILE_CACHE


@pytest.fixture(params=TA_TEST)
def ta_test_fname(request):
    yield request.param


@pytest.fixture
def ta_test(ta_test_fname):
    yield pdc.util.read_csv(ta_test_fname)


@pytest.fixture
def ta_test_all():
    yield tuple(pdc.util.read_csv(x) for x in TA_TEST)


def gen_ta_fixtures():
    for path in TA_TEST + TA_OTHER:

        def fixture_func(file):
            @pytest.fixture
            def _fixture():
                yield pdc.util.read_csv(file)

            return _fixture

        fname = os.path.basename(path).split(".")[0]
        ff = fixture_func(path)
        ff.__name__ = fname
        globals()[ta_fname := f"ta_{fname}"] = ff
        __all__.append(ta_fname)


gen_ta_fixtures()


#########################################################################
## from before the current re-write... unused for now...

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
