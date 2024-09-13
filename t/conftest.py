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


file_dir = "t/asset"
file_names = [
    (file.split(".")[0], os.path.join(root, file))
    for root, _, files in os.walk(file_dir)
    for file in files
    if file.startswith("test") and file.endswith(".csv")
]

for i, (fname, path) in enumerate(file_names, start=1):

    def fixture_func(file=path):
        @pytest.fixture(scope="module")
        def _fixture():
            return pdc.util.read_csv(file)

        return _fixture

    globals()[f"ta_{fname}"] = fixture_func()


@pytest.fixture(scope="module")
def tassets():
    return tuple(pdc.util.read_csv(x) for _, x in file_names)


@pytest.fixture(scope="module", params=file_names)
def passets(request):
    yield pdc.util.read_csv(request.param[1])
