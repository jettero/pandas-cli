#!/usr/bin/env python
# coding: utf-8

from lark import Lark, Transformer, v_args
from .util import say_debug, say_trace, say_error
import pdc.op
from .ptype import Call, Idx, File

grammar = r"""
%import common.DIGIT
%import common.WS
%ignore WS

start: ((assign | implicit_assign) ";")* expr

expr: operation | df

operation: expr "+" expr options -> concat
         | expr "-" expr options -> filter
         | expr "." expr options -> transpocat
         | expr "^" options -> transpose
         | wild_df_seq MAPPING expr -> reduce
         | assign

assign: (tmp|tmp_bump|lhs|rhs) "=" expr
implicit_assign: expr

col: COL_GLOB | IDX

opt: "@"      col ("," col)* -> key
   | "on" "(" col ("," col)* ")" -> key

LDIGIT: "1".."9"
IDX: LDIGIT DIGIT*
MAPPING: ":" | "=>"
COL_GLOB: /[^,@;]+/
NOSLASH_GLOB: /[^\/]+/
NOPARA_GLOB: /[^()]+/

file_glob: "f/" NOSLASH_GLOB "/" | "f(" NOPARA_GLOB ")"
file_wild: "f*"
tmp_wild: "t*"
wild_df: file_wild | tmp_wild | file_glob
wild_df_seq: wild_df ("," wild_df)*

options: opt*
df: file | tmp | lhs | rhs
file: "f" IDX
tmp: "t" IDX
tmp_bump: "T" | "t_" | "t?" | "tt"
lhs: "lhs" | "a"
rhs: "rhs" | "b"
"""


@v_args(inline=True)
class MacroTransformer(Transformer):
    sv_nam = ("lhs", "rhs")

    def __init__(self):
        self.tmpvz = list()
        self.files = list()
        self.sv = list()

    def start(self, *op):
        say_trace(f"MT::start({op!r})")
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
        say_debug(f"MT::concat({op1.short}, {op2.short}, **{opt!r}) -> {c}")
        return c

    def filter(self, op1, op2, opt):
        c = Call(pdc.op.filter, (op1, op2), opt)
        say_debug(f"MT::filter({op1.short}, {op2.short}, {opt!r}) -> {c}")
        return c

    def transpocat(self, op1, op2, opt):
        c = Call(pdc.op.transpocat, (op1, op2), opt)
        say_debug(f"MT::filter({op1.short}, {op2.short}, {opt!r}) -> {c}")
        return c

    def transpose(self, op, opt):
        opt["flags"] = opt.get("flags", dict())
        opt["flags"]["transposed"] = True
        c = Call(pdc.op.transpose, (op,), opt)
        say_debug(f"MT::transpose({op.short}, {opt!r}) -> {c}")
        return c

    def op_idx(self, op, src=None):
        orig_op = op
        if src is None:
            src = self.tmpvz
        op = len(src) + 1 if op in ("+", "-", "") else int(op)
        if op < 1:
            op = 1
        idx = op - 1
        if src is self.tmpvz:
            src_desc = "t?"
        elif src is self.files:
            src_desc = "f?"
        elif src is self.sv:
            try:
                src_desc = self.sv_nam[idx]
            except IndexError:
                src_desc = "sv?"
        else:
            src_desc = "???"
        ret = Idx(op, idx, src_desc, src)
        say_trace(f"MT::op_idx({src_desc[0:1]}{orig_op}) -> {ret}")
        return ret

    def tmp_bump(self):
        return self.op_idx("+")

    def tmp(self, op):
        return self.op_idx(op, src=self.tmpvz)

    def file(self, op):
        return self.op_idx(op, src=self.files)

    def lhs(self):
        return self.op_idx(1, src=self.sv)

    def rhs(self):
        return self.op_idx(2, src=self.sv)

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

    def file_glob(self, op):
        say_debug(f"MT::file_glob({op})")
        return list(self.file(x + 1) for x, df in enumerate(self.files) if df.glob(op))

    def file_wild(self):
        say_debug(f"MT::file_wild()")
        return list(self.file(x + 1) for x in range(len(self.files)))

    def tmp_wild(self):
        say_debug("MT::tmp_wild()")
        return list(self.tmp(x + 1) for x in range(len(self.tmpvz)))

    def wild_df(self, op):
        say_debug(f"MT::wild_df({op!r})")
        return op

    def wild_df_seq(self, *op):
        say_debug(f"MT::wild_df_seq({op})")
        return sum(op, start=list())

    def reduce(self, df, _, op):
        say_debug(f"MT::reduce({df}: {op})")
        lhs = self.lhs()
        rhs = self.rhs()
        ret, *df = df
        for item in df:
            ret = op.replace_args((lhs, ret), (rhs, item))
        return ret


transformer = MacroTransformer()
parser = Lark(grammar, parser="lalr", transformer=transformer)


def parse(statement="f*: a + b", files=None):
    say_debug(f"parse({statement})")
    for item in files:
        if not isinstance(item, File):
            raise ValueError(f"{item} is an invalid pdc.File argument")
    transformer.files = files if isinstance(files, (list, tuple)) else list()
    transformer.tmpvz.clear()
    return parser.parse(statement)
