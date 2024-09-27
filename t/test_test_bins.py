#!/usr/bin/env python
# coding: utf-8

import os


def test_csv_gen(csv1):
    assert os.path.isfile(csv1)


def test_json_gen(json1):
    assert os.path.isfile(json1)
