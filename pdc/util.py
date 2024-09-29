# coding: utf-8

import os
import sys
from collections import namedtuple, OrderedDict
from fnmatch import fnmatch
import pandas as pd


class FileCache(OrderedDict):
    HEADERS_FROM = None

    def set_headers_from(self, hf):
        if hf in (None, False, 0, ""):
            self.HEADERS_FROM = None
            return

        if isinstance(hf, File):
            if hf.fname not in self:
                self[hf.fname] = hf
            self.HEADERS_FROM = hf.fname
            return

        hf = os.path.realpath(hf)
        if hf not in self:
            raise KeyError(f"{hf} appears to not yet be loaded")
        self.HEADERS_FROM = hf

    def add_file(self, fobj, populate_cache=True):
        if populate_cache:
            self[fobj.fname] = fobj
        return fobj

    @property
    def last(self):
        try:
            return next(reversed(self.items()))[-1]
        except StopIteration:
            pass

    @property
    def headers_from(self):
        if self.HEADERS_FROM:
            return self.get(self.HEADERS_FROM)
        return self.last

    @headers_from.setter
    def headers_from(self, v):
        return self.set_headers_from(v)

    def clear(self):
        super().clear()
        self.HEADERS_FROM = None

    reset = clear


FILE_CACHE = FileCache()


class File(namedtuple("File", ["fname", "df", "flags"])):
    def __new__(cls, fname, *a, **kw):
        fname = os.path.realpath(fname)
        return super().__new__(cls, fname, *a, kw)

    def __len__(self):
        return len(self.df)

    def __repr__(self):
        return f"<{os.path.basename(self.fname)}>"

    def __eq__(self, other):
        if isinstance(other, File) and df_compare(self.df, other.df):
            return True
        return False

    def __ne__(self, other):
        return not (self == other)

    @property
    def columns(self):
        return self.df.columns.tolist()

    @property
    def as_list(self):
        return list(sorted(self.df.to_records(index=False).tolist()))

    def glob(self, pat):
        if "**" not in pat and not pat.startswith("/"):
            pat = f"**/{pat}"
        if fnmatch(self.fname, pat):
            say_debug(f"File::glob({self.fname}, {pat}) -> True")
            return True
        say_debug(f"File::glob({self.fname}, {pat}) -> False")


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


def read_csv(fname, headers=None, cache_ok=False, populate_cache=True):
    fname = os.path.realpath(fname)

    if cache_ok and fname in FILE_CACHE:
        # Note that we don't automatically return the cached copy cuz the
        # expectation is that if we specify a file twice on the command-line,
        # we should get two different DataFrame objects.
        #
        # The exception, of course, is where we (re)use the headers from a
        # previous file to populate the columns of some new --csv-nh file.
        return FILE_CACHE[fname]

    if headers is None or headers is True or headers is False:
        df = pd.read_csv(fname)
        return FILE_CACHE.add_file(File(fname, df), populate_cache=populate_cache)

    if isinstance(headers, pd.DataFrame):
        headers = headers.columns.tolist()
    elif isinstance(headers, File):
        headers = headers.columns
    elif isinstance(headers, (tuple, list)):
        pass
    else:
        raise ValueError(f"headers={headers!r} should be a DataFrame, pdc.File, or tuple/list")

    df = pd.read_csv(fname, header=None, names=headers)
    return FILE_CACHE.add_file(File(fname, df, derived_headers=True), populate_cache=populate_cache)


def read_csv_nh(fname):
    # Here, we specifically want to try to re-use the headers from whatever we
    # specified with --headers-from or whatever file was loaded last.
    hf = FILE_CACHE.headers_from
    if not isinstance(hf, File):
        raise KeyError(f"while trying to read {fname} sans headers: unable to locate source for header info")
    return read_csv(fname, headers=hf, populate_cache=False)


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


def say_fatal(*msg):
    say_error(*msg)
    sys.exit(200)
