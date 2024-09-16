#!/usr/bin/env python
# coding: utf-8

import pdc.op

# NOTE: we're mostly testing below to make sure these work without crashing.
# we should also make some accuracy tests...

def test_concat(ta_test_all):
    vv = dict()
    for F in ta_test_all:
        for _, row in F.df.iterrows():
            k, v = row["var"], row["val"]
            if k in vv:
                vv[k].append(v)
            else:
                vv[k] = [v]

    df = ta_test_all[0].df
    for ta in ta_test_all[1:]:
        df = pdc.op.concat(df, ta.df)
    for _, row in df.iterrows():
        k, v = row["var"], row["val"]
        assert v in vv[k]


def test_transpocat(ta_test1, ta_test2):
    df = pdc.op.transpocat(ta_test1.df, ta_test2.df, key="var", merge_type="outer")
    c = df.columns.tolist()

    assert c == ["var", "val", "ext"]

    df = pdc.op.transpocat(ta_test1.df, ta_test2.df)
    c = df.columns.tolist()

    assert c == ["var", "val", "ext"]

def test_filter(ta_test1, ta_test2):
    df = pdc.op.filter(ta_test1.df, ta_test2.df, key="var")
    ldf = len(df)
    lta = len(ta_test1.df)

    assert ldf == lta -1
