#!/usr/bin/env python
# coding: utf-8

import os
import inspect
from lark import Lark, Transformer, v_args
from .ptype import TypedFileName, File

grammar = r"""
start: filename -> fname
     | ":" filename -> fname_hf_last
     | filename ":" filename -> fname_hf_named

filename: PATH_CHARS -> boring_fname
        | PATH_CHARS "@" TYPE_CHARS -> typed_fname

ESCAPED_SLASH: "\\"
ESCAPED_ATPERSAND: "\@"
ESCAPED_COLON: "\:"

PATH_CHAR: ESCAPED_SLASH | ESCAPED_ATPERSAND | ESCAPED_COLON | /[^\\@:]/
PATH_CHARS: PATH_CHAR+
TYPE_CHAR: /[a-zA-F0-9]/
TYPE_CHARS: TYPE_CHAR+
"""


@v_args(inline=True)
class MacroTransformer(Transformer):
    LAST_FILE = None

    def boring_fname(self, fname):
        return TypedFileName.grok(str(fname))

    def typed_fname(self, fname, ftype):
        return TypedFileName.grok(str(fname), str(ftype))

    def fname_hf_last(self, tfn):
        if isinstance(self.LAST_FILE, TypedFileName):
            return TypedFileName.grok(tfn.fname, tfn.ftype, self.LAST_FILE)
        raise KeyError(f"no preceeding file to source from wrt {tfn.fname}")

    def fname_hf_named(self, src_tfn, tfn):
        return TypedFileName.grok(tfn.fname, tfn.ftype, src_tfn)

    def fname(self, tfn):
        return tfn


transformer = MacroTransformer()
parser = Lark(grammar, parser="lalr", transformer=transformer)


def grok_fname(fname, last_file=None):
    if isinstance(last_file, TypedFileName):
        transformer.LAST_FILE = last_file
    elif isinstance(last_file, File):
        transformer.LAST_FILE = parser.parse(last_file.fname)
    elif last_file is not None:
        transformer.LAST_FILE = parser.parse(last_file)
    else:
        transformer.LAST_FILE = None
    return parser.parse(fname)
