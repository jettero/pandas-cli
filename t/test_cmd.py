#!/usr/bin/env python
# coding: utf-8

import pytest
import pdc.cmd


def test_csv_args(FILE_CACHE, ta_test1):
    FILE_CACHE.clear()

    args = pdc.cmd.populate_args("t/asset/test1.csv")
    (test1,) = args.files

    assert FILE_CACHE.last is test1
    assert test1.as_list == ta_test1.as_list


def test_csv_nh_args_via_last(FILE_CACHE, ta_test1):
    FILE_CACHE.clear()

    args = pdc.cmd.populate_args("t/asset/test1.csv", ":t/asset/test1_nh.csv")
    test1, test1_nh = args.files

    assert FILE_CACHE.last is test1

    assert test1.columns == test1_nh.columns
    assert test1.as_list == ta_test1.as_list
    assert test1_nh.as_list == ta_test1.as_list


def test_csv_nh_not_enough_args(FILE_CACHE):
    FILE_CACHE.clear()

    with pytest.raises(KeyError):
        pdc.cmd.populate_args(":t/asset/test1_nh.csv")


def test_csv_nh_args_via_last(FILE_CACHE, ta_test1):
    FILE_CACHE.clear()

    args = pdc.cmd.populate_args(
        "t/asset/test1.csv",
        "t/asset/test2.csv",
        "test1.csv:t/asset/test1_nh.csv",
    )

    test1, test2, test1_nh = args.files

    assert ta_test1.as_list == test1.as_list
    assert ta_test1.as_list == test1_nh.as_list
    assert test1.columns == test1_nh.columns
