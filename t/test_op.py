#!/usr/bin/env python
# coding: utf-8

import pdc.op


def test_concat(ta_test_all):
    vv = dict()
    for F in ta_test_all:
        for _, row in F.df.iterrows():
            k, v = row["var"], row["val"]
            if k in vv:
                vv[k].append(v)
            else:
                vv[k] = [v]

    df = pdc.op.concat(*(x.df for x in ta_test_all))
    for _, row in df.iterrows():
        k, v = row["var"], row["val"]
        assert v in vv[k]


def test_merge_specified(ta_test1, ta_test2):
    df = pdc.op.transpocat(ta_test1.df, ta_test2.df, key="var", merge_type="outer")
    c = df.columns.tolist()

    assert c == ["var", "val", "ext"]


def test_merge_unspecified(ta_test1, ta_test2):
    df = pdc.op.transpocat(ta_test1.df, ta_test2.df, merge_type="outer")
    c = df.columns.tolist()

    assert c == ["var", "val", "ext"]
