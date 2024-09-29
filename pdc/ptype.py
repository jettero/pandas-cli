#!/usr/bin/env python
# coding: utf-8

from collections import namedtuple
from .util import say_trace, say_error, File


class Call(namedtuple("Call", ["fn", "args", "kw"])):
    def __call__(self):
        say_trace(f"Call(): {self}")
        args = [x().df for x in self.args]
        name = " ".join([self.fn.__name__, *(str(x) for x in args)])
        return File(name, self.fn(*args, **self.kw))

    def __repr__(self):
        f = self.fn
        fn = f"{f.__module__}.{f.__name__}"
        return f"{fn}(*{self.args!r}, **{self.kw!r})"

    def replace_args(self, *args):
        return Call(self.fn, args, self.kw)


class Idx(namedtuple("Idx", ["op", "idx", "snam", "src"])):
    def __call__(self):
        say_trace(f"Idx(): {self}")
        try:
            res = self.src[self.idx]
            if isinstance(res, (Call, Idx)):
                return res()
            return res
        except IndexError:
            say_error(f"{self} points to nothing")

    def __eq__(self, other):
        if isinstance(other, Idx):
            if self.op != other.op:
                return False
            if self.src is not other.src:
                return False
            return True

    @property
    def deref(self):
        return self.src[self.idx]

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
