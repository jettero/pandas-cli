#!/usr/bin/env python
# coding: utf-8

import os
import pytest

from test.bin.gen_csv import main as gen_csv
from test.bin.gen_json import main as gen_json

from pandas_cli.magic_buffer import MagicBuffer


@pytest.fixture
def csv1(filename="test/output/1.csv"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    gen_csv("--output-file", filename)
    yield filename
    os.unlink(filename)


@pytest.fixture
def json1(filename="test/output/1.json"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    gen_csv("--output-file", filename)
    yield filename
    os.unlink(filename)


@pytest.fixture
def csv1_fh(csv1):
    yield open(csv1, "r")


@pytest.fixture
def json1_fh(json1):
    yield open(json1, "r")


@pytest.fixture
def csv1_mb(csv1_fh):
    yield MagicBuffer(csv1_fh)


@pytest.fixture
def json1_mb(json1_fh):
    yield MagicBuffer(json1_fh)
