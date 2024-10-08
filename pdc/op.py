#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from .util import say_warn, xlate_column_labels

DING_DING_DING = "\x07\x07\x07"  # ding ding ding


def concat(A, B, key=None):
    #  aaa   bbb   aaa
    #  aaa + bbb = aaa
    #  aaa   bbb   aaa
    #              bbb
    #              bbb
    #              bbb
    df = pd.concat((A, B), ignore_index=True)
    # NOTE: concat() is different than a join, if we do want to use the key for
    # left/inner/right join behavior then it's really a dedup after the fact.
    if key is None:
        return df
    elif isinstance(key, list):
        pass
    elif isinstance(key, (tuple, set)):
        key = xlate_column_labels(B, *key)
    elif isinstance(key, str):
        key = xlate_column_labels(B, key)
    else:
        raise ValueError(f"key={key} is invalid. should be a tuple of strings or something")
    return df.drop_duplicates(subset=key, keep="last")


def transpose(A):
    return A.transpose()


def transpocat(A, B, key=None, merge_type="outer"):
    # XXX: maybe this is 'append' or 'sidepend'? ... I just really like this word transpocat.
    #  aaa   bbb   aaabbb
    #  aaa + bbb = aaabbb
    #  aaa   bbb   aaabbb
    if key is None:
        key = A.columns.tolist()
    elif isinstance(key, list):
        pass
    elif isinstance(key, (tuple, set)):
        key = xlate_column_labels(B, *key)
    elif isinstance(key, str):
        key = xlate_column_labels(B, key)
    else:
        raise ValueError(f"key={key} is invalid. should be a tuple of strings or something")
    A = pd.merge(A, B, on=key, suffixes=("", DING_DING_DING), how=merge_type)
    c = A.columns.tolist()
    d = [x for x in c if f"{x}{DING_DING_DING}" in c]
    for lhs in d:
        A[lhs] = A[lhs].combine_first(A[f"{lhs}{DING_DING_DING}"])
    return A.drop(columns=[f"{x}{DING_DING_DING}" for x in d])


def filter(A, B, key=None):
    #  axx   ayy   bxx
    #  bxx - dyy = cxx
    #  cxx   eyy
    if key is None:
        key = A.columns.tolist()
    elif isinstance(key, list):
        pass
    elif isinstance(key, (tuple, set)):
        key = xlate_column_labels(B, *key)
    elif isinstance(key, str):
        key = xlate_column_labels(B, key)
    else:
        raise ValueError(f"key={key} is invalid. should be a tuple of strings or something")
    A["unique_key"] = A[key].apply(tuple, axis=1)
    B["unique_key"] = B[key].apply(tuple, axis=1)
    return A[~A.unique_key.isin(B.unique_key)].drop(columns="unique_key")
