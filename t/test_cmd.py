#!/usr/bin/env python
# coding: utf-8

import pdc.cmd


def test_csv_args(ta_test1):
    args = pdc.cmd.populate_args("--csv", "t/asset/test1.csv")
    for item in args.files:
        assert item == ta_test1
    # assert args.files == [ta_test1]
