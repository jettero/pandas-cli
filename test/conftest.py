#!/usr/bin/env python
# coding: utf-8

import os
import pytest

from test.bin.gen_csv  import main as gen_csv
from test.bin.gen_json import main as gen_json

@pytest.fixture
def csv1(filename="test/output/1.csv"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    gen_csv('--output-file', filename)
    yield filename
    os.unlink(filename)

@pytest.fixture
def json1(filename="test/output/1.json"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    gen_csv('--output-file', filename)
    yield filename
    os.unlink(filename)
