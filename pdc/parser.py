#!/usr/bin/env python
# coding: utf-8

from collections import namedtuple
from lark import Lark, Transformer, v_args
from .util import File, say_debug, say_trace
import pdc.op

grammar = """
%import common.CNAME
%import common.NUMBER
%import common.WS
%ignore WS

start: ((assign | implicit_assign) ";")* expr

expr: operation | df

operation: expr "+" expr options -> concat
         | assign

assign: (tmp|tmp_bump) "=" expr
implicit_assign: expr

opt: "@"      CNAME ("," CNAME)* -> key
   | "on" "(" CNAME ("," CNAME)* ")" -> key

options: opt*

df: file | tmp

file: "f" NUMBER -> op_idx_files
tmp: "t" NUMBER -> op_idx_tmp
tmp_bump: "t+"
"""


class Call(namedtuple("Call", ["fn", "args", "kw"])):
    def __call__(self):
        say_trace(f"Call(): {self}")
        args = [x() if callable(x) else x for x in self.args]
        kw = {k: v() if callable(v) else v for k, v in self.kw.items()}
        name = " ".join([self.fn.__name__, *(str(x) for x in args)])
        return File(name, self.fn(*args, **kw))

    def __repr__(self):
        f = self.fn
        fn = f"{f.__module__}.{f.__name__}"
        return f"{fn}(*{self.args!r}, **{self.kw!r})"


class Idx(namedtuple("Idx", ["op", "idx", "snam", "src"])):
    def __call__(self):
        say_trace(f"Idx(): {self}")
        try:
            res = self.src[self.idx]
            if callable(res):
                return res()
            return res
        except IndexError:
            say_warn(f"{self} points to nothing")

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


@v_args(inline=True)
class MacroTransformer(Transformer):
    def __init__(self):
        self.tmpvz = list()
        self.files = list()

    def start(self, *op):
        return op[-1]

    def key(self, *op):
        say_trace(f"MT::key({op!r})")
        return "key", set(str(o) for o in op)

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

    @property
    def tid(self):
        return len(self.tmpvz)

    def op_idx_files(self, op):
        return self.op_idx(op, self.files)

    def op_idx_tmp(self, op):
        return self.op_idx(op, self.tmpvz)

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
        return self.op_idx_tmp("+")

    def tmp(self, op):
        t = self.op_idx_tmp(op)
        return t

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
