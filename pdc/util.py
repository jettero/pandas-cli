# coding: utf-8

import os
import sys
from collections import namedtuple
from fnmatch import fnmatch
import pandas as pd


class File(namedtuple("File", ["fname", "df", "flags"])):
    def __new__(cls, *a, **kw):
        return super().__new__(cls, *a, kw)

    def __len__(self):
        return len(self.df)

    def __repr__(self):
        return f"<{os.path.basename(self.fname)}>"

    @property
    def columns(self):
        return self.df.columns.tolist()

    def __eq__(self, other):
        if isinstance(other, File) and df_compare(self.df, other.df):
            return True
        return False

    def __ne__(self, other):
        return not (self == other)


def xlate_column_labels(df, *items):
    cols = df.columns if isinstance(df, File) else df.columns.tolist()
    ret = set()
    for item in items:
        if isinstance(item, int):
            ret.add(cols[item - 1])
        elif "*" in item:
            for c in cols:
                if fnmatch(c, item):
                    ret.add(c)
        else:
            ret.add(item)
    return list(sorted(ret))


def df_sorted_records(*df):
    for item in df:
        if isinstance(item, File):
            item = item.df
        yield sorted(item.to_records(index=False).tolist())


def df_zipper(*df, strict=False):
    yield from zip(*df_sorted_records(*df), strict=strict)


def df_compare(*df):
    # NOTE: we use this df_compare function in tests and they're handy for
    # that. but if these inputs were large, the below would be inefficient.
    try:
        for item0, *items in df_zipper(*df, strict=True):
            for item in items:
                if item0 != item:
                    return False
    except ValueError as e:
        return False  # zipper strict=True raises a ValueError when length differs
    return True


def special_list_sort(*args):
    """generate a sorting function that prepends a score to the sort items"""

    def inner(x):
        score = 99
        for i, item in enumerate(args):
            if x == item or x in item:
                score = i
                break
        return f"{score:02d}{x}"

    return inner


def read_csv(fname, headers=None):
    if headers is None or headers is True or headers is False:
        df = pd.read_csv(fname)
        return File(fname, df)

    if isinstance(headers, pd.DataFrame):
        headers = headers.columns.tolist()
    elif isinstance(headers, File):
        headers = headers.columns
    elif isinstance(headers, (tuple, list)):
        pass
    else:
        raise ValueError(f"headers={headers!r} should be a DataFrame, pdc.File, or tuple/list")
    df = pd.read_csv(fname, header=None, names=headers)
    return File(fname, df, derived_headers=True)


SAY_TRACE = 0
SAY_DEBUG = SAY_TRACE + 1
SAY_INFO = SAY_DEBUG + 1
SAY_WARN = SAY_INFO + 1
SAY_ERROR = SAY_WARN + 1
SAY_LEVEL = SAY_ERROR
SAY_WORDS = "TRACE DEBUG INFO WARN ERROR".split()


def set_say_level(x=None):
    global SAY_LEVEL
    try:
        x = x if x is not None else os.environ["PDC_SAY_LEVEL"]
        try:
            x = x.upper()
            x = SAY_WORDS.index(x)
        except (ValueError, AttributeError):
            x = int(x)
        SAY_LEVEL = max(SAY_TRACE, min(x, SAY_ERROR))
    except (KeyError, ValueError):
        SAY_LEVEL = SAY_ERROR
    return SAY_LEVEL


set_say_level()


SAY_TRIGGER = bytes([87, 84, 70]).decode()


def say(*msg, level=SAY_INFO):
    level = max(SAY_TRACE, min(level, SAY_ERROR))
    if level >= SAY_LEVEL or any(SAY_TRIGGER in s for s in msg):
        print(f"[{SAY_WORDS[level]}]", *msg, file=sys.stderr)


def say_trace(*msg):
    say(*msg, level=SAY_TRACE)


def say_debug(*msg):
    say(*msg, level=SAY_DEBUG)


def say_info(*msg):
    say(*msg, level=SAY_INFO)


def say_warn(*msg):
    say(*msg, level=SAY_WARN)


say_warning = say_warn


def say_error(*msg):
    say(*msg, level=SAY_ERROR)
