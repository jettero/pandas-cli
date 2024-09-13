#!/usr/bin/env python
# coding: utf-8

import pdc.op


def test_concat(tassets):
    vv = dict()
    for F in tassets:
        for _, row in F.df.iterrows():
            k, v = row["var"], row["val"]
            if k in vv:
                vv[k].append(v)
            else:
                vv[k] = [v]

    df = pdc.op.concat(*tassets)
    for _, row in df.iterrows():
        k, v = row["var"], row["val"]
        assert v in vv[k]
