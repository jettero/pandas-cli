#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from .util import say_warn

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
    if key is not None:
        return df.drop_duplicates(subset=(key if isinstance(key, (list, tuple)) else tuple(key)), keep="last")
    return df


def transpocat(A, B, key=None, merge_type="outer"):
    #  aaa   bbb   aaabbb
    #  aaa + bbb = aaabbb
    #  aaa   bbb   aaabbb
    if key is None:
        k = A.columns.tolist()
    A = pd.merge(A, B, on=key, suffixes=("", DING_DING_DING), how=merge_type)
    c = A.columns.tolist()
    d = [x for x in c if f"{x}{DING_DING_DING}" in c]
    for lhs in d:
        A[lhs] = A[lhs].combine_first(A[f"{lhs}{DING_DING_DING}"])
    return A.drop(columns=[f"{x}{DING_DING_DING}" for x in d])


def filter(*df, **kw):  # pragma: no cover
    #  axy   def   axy
    #  bwj - ghi = ckl
    #  ckl   baz
    return concat(*df, **kw)
    # if args.mode == "A-cat":
    #     B = pd.concat((x.df for x in args.files[1:]), ignore_index=True)
    #     A = args.files[0].df
    #     k = args.unique if args.unique else HEADERS
    #     if len(k) == 1:
    #         k = k[0]
    #         qprint(
    #             f'filtering items from {args.files[0].fname} based on "{k}" values '
    #             f"from {', '.join(x.fname for x in args.files[1:])}"
    #         )
    #         return output(A[~A[k].isin(B[k])])
    #     if len(k) > 1:
    #         A["unique_key"] = A[k].apply(tuple, axis=1)
    #         B["unique_key"] = B[k].apply(tuple, axis=1)
    #         qprint(
    #             f'filtering items from {args.files[0].fname} based on "{k}" values '
    #             f"from {', '.join(x.fname for x in args.files[1:])}"
    #         )
    #         return output(A[~A.unique_key.isin(B.unique_key)].drop(columns="unique_key"))
