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

    @property
    def deref(self):
        return self.src[self.idx]

    @property
    def short(self):
        return f"{{{self.snam[0:1]}{self.op}}}"

    def __repr__(self):
        try:
            v = self.src[self.idx]
        except IndexError:
            v = "∅"
        return f"{{{self.snam[0:1]}{self.op}:{v}}}"
