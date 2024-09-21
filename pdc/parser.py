#!/usr/bin/env python
# coding: utf-8

from lark import Lark, Transformer, v_args
from .util import say_debug, say_trace, say_error
import pdc.op
from .ptype import Call, Idx, File

grammar = """
%import common.CNAME
%import common.DIGIT
%import common.WS
%ignore WS

start: ((assign | implicit_assign) ";")* expr

expr: operation | df

operation: expr "+" expr options -> concat
         | expr "-" expr options -> filter
         | assign

assign: (tmp|tmp_bump) "=" expr
implicit_assign: expr

col: CNAME | IDX

opt: "@"      col ("," col)* -> key
   | "on" "(" col ("," col)* ")" -> key

options: opt*

df: file | tmp

LDIGIT: "1".."9"
IDX: LDIGIT DIGIT*

file: "f" IDX
tmp: "t" IDX
tmp_bump: "t+"
"""


@v_args(inline=True)
class MacroTransformer(Transformer):
    def __init__(self):
        self.tmpvz = list()
        self.files = list()

    def start(self, *op):
        return op[-1]

    def col(self, op):
        say_trace(f"MT::col({op!r})")
        try:
            return int(op)
        except ValueError:
            pass
        return str(op)

    def key(self, *op):
        say_trace(f"MT::key({op!r})")
        return "key", set(op)

    def options(self, *op):
        say_trace(f"MT::options({op!r})")
        kw = dict()
        for k, v in op:
            kw[k] = kw[k] | v if k in kw else v
        return kw

    def concat(self, op1, op2, opt):
        c = Call(pdc.op.concat, (op1, op2), opt)
        say_debug(f"MT::concat({op1.short}, {op2.short}, {opt!r}) -> {c}")
        return c

    def filter(self, op1, op2, opt):
        c = Call(pdc.op.filter, (op1, op2), opt)
        say_debug(f"MT::filter({op1.short}, {op2.short}, {opt!r}) -> {c}")
        return c

    def op_idx(self, op, src=None):
        orig_op = op
        if src is None:
            src = self.tmpvz
        if src is self.tmpvz:
            src_desc = "tmpvz"
        elif src is self.files:
            src_desc = "files"
        else:
            src_desc = "?????"
        op = len(src) + 1 if op in ("+", "-", "") else int(op)
        if op < 1:
            op = 1
        idx = op - 1
        ret = Idx(op, idx, src_desc, src)
        say_trace(f"MT::op_idx({src_desc[0:1]}{orig_op}) -> {ret}")
        return ret

    def tmp_bump(self):
        return self.op_idx("+")

    def tmp(self, op):
        return self.op_idx(op, src=self.tmpvz)

    def file(self, op):
        return self.op_idx(op, src=self.files)

    def df(self, op):
        return op

    def expr(self, op):
        say_debug(f"MT::expr(op={op})")
        return op

    def implicit_assign(self, op2):
        say_debug(f"MT::implicit_assign({op2})")
        t = self.tmp_bump()
        return self.assign(t, op2)

    def assign(self, op1, op2):
        while len(op1.src) < op1.op:
            op1.src.append(None)
        op1.src[op1.idx] = op2
        say_debug(f"MT::assign({op1.short}, {op2}) -> {op1}")
        return op1


transformer = MacroTransformer()
parser = Lark(grammar, parser="lalr", transformer=transformer)


def parse(statement="r(f*: a+b)", files=None):
    for item in files:
        if not isinstance(item, File):
            raise ValueError(f"{item} is an invalid pdc.File argument")
    transformer.files = files if isinstance(files, (list, tuple)) else list()
    return parser.parse(statement)
