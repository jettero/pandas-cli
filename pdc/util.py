# coding: utf-8

import os
import sys
import re
from fnmatch import fnmatch
import pandas as pd
from .fname_parser import grok_fname
from .ptype import TypedFileName, File, FILE_CACHE


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


def df_zipper(*df, strict=False):
    yield from zip(*(x.to_records(index=False).tolist() for x in df), strict=strict)


def df_compare(*df):
    # NOTE: we use this df_compare function in tests and they're handy for
    # that. but if these inputs were large, the below would be inefficient.
    try:
        for item0, *items in df_zipper(*df, strict=True):
            for item in items:
                if item0 != item:
                    say_debug(f"{item0} != {item}")
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


def read_csv(fname, cache_ok=False, populate_cache=True, globby_ok=True):
    say_debug(f"util::read_csv({fname}, cache_ok={cache_ok}, populate_cache={populate_cache}, globby_ok={globby_ok})")
    return read_file(f"{fname}@csv", cache_ok=cache_ok, populate_cache=populate_cache)


def read_file(fname, cache_ok=False, populate_cache=True, globby_ok=False):
    say_debug(f"util::read_file({fname}, cache_ok={cache_ok}, populate_cache={populate_cache}, globby_ok={globby_ok})")
    if isinstance(fname, TypedFileName):
        tfn = fname
    else:
        tfn = grok_fname(fname, last_file=FILE_CACHE.last)
        say_debug(f"util::read_file() translated {fname} to {tfn}")
    fname = tfn.fname

    if cache_ok:
        if tfn.fname in FILE_CACHE:
            # Note that we don't automatically return the cached copy cuz the
            # expectation is that if we specify a file twice on the command-line,
            # we should get two different DataFrame objects.
            #
            # The exception, of course, is where we (re)use the headers from a
            # previous file to populate the columns of some new file.
            say_debug(f"util::read_file() found cached entry for {tfn.fname}")
            return FILE_CACHE[tfn.fname]

        if globby_ok:
            for item in FILE_CACHE.values():
                if item.glob(tfn.fname):
                    say_debug(f"util::read_file() found cached entry by globby for {tfn.fname}")
                    return item

    # XXX: excel and json formats may need additional options. we have no
    # syntax for that.

    # XXX: this header source business is very csv oriented.  I did confirm
    # that the headers=None, names=() thing will work for read_excel, it won't
    # for read_json.

    hkw = dict()
    if tfn.hsrc is not None:
        hf = read_file(tfn.hsrc, cache_ok=True, populate_cache=False, globby_ok=True)
        hkw["header"] = None
        hkw["names"] = hf.columns

    if tfn.ftype == "csv":
        df = pd.read_csv(tfn.fname, **hkw)

    elif tfn.ftype == "tsv":
        df = pd.read_csv(tfn.fname, sep="\t", **hkw)

    elif tfn.ftype == "excel":
        df = pd.read_excel(tfn.fname, **hkw)

    elif tfn.ftype == "json":
        if hkw:
            raise ValueError(
                "fname={tfn.fname}'s filetype={tfn.ftype} but only csv, tsv, and excel are supported when header source is specified"
            )
        df = pd.read_json(tfn.fname)

    else:
        raise ValueError("fname={tfn.fname}'s filetype={tfn.ftype} not (yet?) supported")

    return FILE_CACHE.add_file(File(fname, df, derived_headers=bool(hkw)), populate_cache=populate_cache)


####################################################
SAY_TRACE = 0
SAY_DEBUG = SAY_TRACE + 1
SAY_INFO = SAY_DEBUG + 1
SAY_WARN = SAY_INFO + 1
SAY_ERROR = SAY_WARN + 1
SAY_LEVEL = SAY_ERROR
SAY_WORDS = "TRACE DEBUG INFO WARN ERROR".split()
SAY_TRIGGER = bytes([87, 84, 70]).decode()  # if this is in any say string, we print no matter what the other settings


def say(*msg, level=SAY_INFO):
    level = max(SAY_TRACE, min(level, SAY_ERROR))
    if level >= SAY_LEVEL or any(SAY_TRIGGER in s for s in msg):
        print(f"[{SAY_WORDS[level]}]", *msg, file=sys.stderr, flush=True)


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


def set_say_level(x=None):
    global SAY_LEVEL
    try:
        x = x if x is not None else os.environ["PDC_SAY_LEVEL"]
        try:
            if (y := int(x)) < 0:
                x = SAY_LEVEL + y  # actually minus, eg y=-6
        except ValueError:
            pass
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
