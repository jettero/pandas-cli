#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from .util import File


def concat(*df, **kw):
    if not kw:
        kw["ignore_index"] = True
    return pd.concat((x.df if isinstance(x, File) else x for x in df), **kw)


def column_merge(*df):
    return concat(*df)
    # if args.mode == "column-merge":
    #     A = args.files[0].df
    #     k = args.unique
    #     if not args.unique:
    #         qprint(f"key columns unspecified, guessing")
    #         k = [x for x in HEADERS if x.endswith("id")]
    #         if not k:
    #             k = HEADERS
    #     qprint(f"merging all columns (keyed on {'-'.join(sorted(k))}) starting with {args.files[0].fname}")
    #     DING_DING_DING = "\x07\x07\x07"  # ding ding ding
    #     for fname, B in args.files[1:]:
    #         qprint(f"  merge in the columns of {fname}")
    #         A = pd.merge(A, B, on=k, suffixes=("", DING_DING_DING), how=args.merge_type)
    #         c = A.columns.tolist()
    #         d = [x for x in c if f"{x}{DING_DING_DING}" in c]
    #         for lhs in d:
    #             A[lhs] = A[lhs].combine_first(A[f"{lhs}{DING_DING_DING}"])
    #         A = A.drop(columns=[f"{x}{DING_DING_DING}" for x in d])
    #     return output(A)


def left_join(*df):
    return concat(*df)
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
