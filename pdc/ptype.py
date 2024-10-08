#!/usr/bin/env python
# coding: utf-8

import os
from collections import namedtuple, OrderedDict
from fnmatch import fnmatch
import pdc.util

FILE_TYPES = ("csv", "tsv", "json", "excel")
EXT_FILE_MAP = {
    "js": "json",
    "xlsx": "excel",
    "xls": "excel",
    "yml": "yaml",
}


class Call(namedtuple("Call", ["fn", "args", "kw"])):
    def __call__(self):
        pdc.util.say_trace(f"Call(): {self}")
        args = [x().df for x in self.args]
        name = " ".join([self.fn.__name__, *(str(x) for x in args)])
        kwargs = self.kw.copy()
        try:
            flags = kwargs.pop("flags")
        except KeyError:
            flags = dict()
        return File(name, self.fn(*args, **kwargs), **flags)

    def __repr__(self):
        f = self.fn
        fn = f"{f.__module__}.{f.__name__}"
        return f"{fn}(*{self.args!r}, **{self.kw!r})"

    def replace_args(self, *todo):
        args = self.args
        for orig, nv in todo:
            args = [nv if x == orig else x for x in args]
        args = [x.replace_args(*todo) if isinstance(x, Call) else x for x in args]
        return Call(self.fn, args, self.kw)


class Idx(namedtuple("Idx", ["op", "idx", "snam", "src"])):
    def __call__(self):
        pdc.util.say_trace(f"Idx(): {self}")
        try:
            res = self.src[self.idx]
            if isinstance(res, (Call, Idx)):
                return res()
            return res
        except IndexError:
            pdc.util.say_error(f"{self} points to nothing")

    def __eq__(self, other):
        if isinstance(other, Idx):
            if self.op != other.op:
                return False
            if self.src is not other.src:
                return False
            return True

    @property
    def deref(self):
        ret = self.src[self.idx]
        if isinstance(ret, Idx):
            return ret.deref
        return ret

    @property
    def short(self):
        if self.snam.endswith("?"):
            return f"{{{self.snam[:-1]}{self.op}}}"
        return f"{{{self.snam}}}"

    def __repr__(self):
        try:
            v = self.src[self.idx]
        except IndexError:
            v = "∅"
        if self.snam.endswith("?"):
            return f"{{{self.snam[:-1]}{self.op}:{v}}}"
        return f"{{{self.snam}:{v}}}"


def ftypeize(x):
    if isinstance(x, str):
        x = x.lower()
        x = EXT_FILE_MAP.get(x, x)
    return x


class TypedFileName(namedtuple("TypedFileName", ["fname", "ext", "ftype", "hsrc"])):
    @classmethod
    def grok(cls, fname, ftype=None, hsrc=None):
        oftype = ftype
        try:
            _, ext = fname.rsplit(".", maxsplit=1)  # ValueError when no extension
            ext = ftypeize(ext)
        except (AttributeError, ValueError):
            ext = None
        ftype = ftypeize(ftype) if ftype else ftypeize(ext)
        if ftype not in FILE_TYPES:
            raise ValueError(f"unsupported file type {ftype} -- fname={fname}, ftype={oftype}, ext={ext}")
        return cls(fname, ext, ftype, hsrc)


class FileCache(OrderedDict):
    @property
    def last(self):
        for fname, fobj in reversed(self.items()):
            if not fobj.has("derived_headers"):
                return fobj

    def add_file(self, fobj, populate_cache=True):
        if populate_cache:
            self[fobj.fname] = fobj
        return fobj

    def clear(self):
        super().clear()

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
        if isinstance(other, File) and pdc.util.df_compare(self.df, other.df):
            return True
        return False

    def __ne__(self, other):
        return not (self == other)

    @property
    def columns(self):
        return self.df.columns.tolist()

    @property
    def as_list(self):
        return self.df.to_records(index=False).tolist()

    records = as_list

    def to_records(self, *a, **kw):
        return self.df.to_records(*a, **kw)

    def has(self, flag):
        if self.flags.get(flag, False):
            return True
        return False

    def glob(self, pat):
        if "**" not in pat and not pat.startswith("/"):
            pat = f"**/{pat}"
        if fnmatch(self.fname, pat):
            pdc.util.say_debug(f"File::glob({self.fname}, {pat}) -> True")
            return True
        pdc.util.say_debug(f"File::glob({self.fname}, {pat}) -> False")
