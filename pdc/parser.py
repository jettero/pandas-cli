#!/usr/bin/env python
# coding: utf-8

from collections import namedtuple
from lark import Lark, Transformer, v_args

File = namedtuple("File", ["df", "filename", "path"])

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
        return ("concat", op1, op2)

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


def parse(statement="r(f*: a+b)", *files, resolv_tmp=True):
    transformer.resolv_tmp = resolv_tmp
    for item in files:
        if not isinstance(item, File):
            raise ValueError(f"{item} is an invalid pdc.parser.File argument")
    transformer.files = files
    return parser.parse(statement)
