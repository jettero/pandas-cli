#!/usr/bin/env python
# coding: utf-8

from collections import namedtuple
from lark import Lark, Transformer, v_args
from .util import File
import pdc.op

grammar = """
%import common.CNAME
%import common.NUMBER
%import common.WS
%ignore WS

start: texpr (";" texpr)*

texpr: expr

expr: operation | df

operation: expr "+" expr opt* -> concat

opt: "@" CNAME -> key
   | "on" "(" CNAME ")" -> key

df: file | tmp

file: "f" NUMBER
tmp: "t" NUMBER
"""


class Call(namedtuple("Call", ["fn", "args", "kw"])):
    def __call__(self):
        args = [x() if callable(x) else x for x in self.args]
        print(f"exec({self!r})")
        return self.fn(*args, **self.kw)

    def __repr__(self):
        return f"{self.fn.__module__}.{self.fn.__name__}(*{self.args!r}, **{self.kw!r})"


def _op_idx(op):
    op = int(op)
    idx = op - 1
    return op, idx


@v_args(inline=True)
class MacroTransformer(Transformer):
    def __init__(self, resolv_tmp=True):
        self.resolv_tmp = resolv_tmp
        self.tmp_items = list()
        self.files = list()

    def start(self, *op):
        return op[-1]

    def key(self, name):
        return ("key", str(name))

    def concat(self, op1, op2, *opt):
        kw = {k: v for o in opt for k, v in zip(o[::2], o[1::2])}
        return Call(pdc.op.concat, (op1, op2), kw)

    def file(self, op):
        op, idx = _op_idx(op)
        return self.files[idx]

    def tmp(self, op=None):
        if op is None:
            op = len(self.tmp_items)
        op, idx = _op_idx(op)
        if self.resolv_tmp:
            return self.tmp_items[idx]
        return ("tmp", op, self.tmp_items[idx])

    def df(self, op):
        return op

    def expr(self, op):
        return op

    def assign(self, val):
        self.tmp_items.append(val)
        return self.tmp()

    def texpr(self, op):
        return self.assign(op)


transformer = MacroTransformer()
parser = Lark(grammar, parser="lalr", transformer=transformer)


def parse(statement="r(f*: a+b)", files=None, resolv_tmp=True):
    transformer.resolv_tmp = resolv_tmp
    for item in files:
        if not isinstance(item, File):
            raise ValueError(f"{item} is an invalid pdc.File argument")
    transformer.files = files if isinstance(files, (list, tuple)) else list()
    return parser.parse(statement)
