#!/usr/bin/env python
# coding: utf-8

from collections import namedtuple
from lark import Lark, Transformer, v_args
from .util import File
import pdc.op

grammar = """
start: texpr (";" texpr)*

texpr: expr

expr: operation | df

operation: expr "+" expr -> concat
         | expr "*" expr -> join
         | expr "-" expr -> filter

df: file | tmp

file: "f" NUMBER
tmp: "t" NUMBER

%import common.NUMBER
FILENAME_GLOB: /[a-zA-Z0-9*._-]+/
MACRO_EXPRESSION_ARG: /[a-z]/
%import common.WS
%ignore WS
"""


class Call(namedtuple("Call", ["fn", "args"])):
    def __call__(self):
        args = [x() if callable(x) else x for x in self.args]
        return self.fn(*args)

    def __repr__(self):
        return f"{self.fn.__module__}.{self.fn.__name__}{tuple(self.args)}"


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

    def concat(self, op1, op2):
        return Call(pdc.op.concat, (op1, op2))

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
