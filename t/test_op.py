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

    df = pdc.op.concat(*ta_test_all)
    for _, row in df.iterrows():
        k, v = row["var"], row["val"]
        assert v in vv[k]
