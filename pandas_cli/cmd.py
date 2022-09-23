#!/usr/bin/env python
# coding: utf-8

import sys
import argparse
import pandas as pd
from .version import __version__ as VERSION
from .magic_buffer import MagicBuffer

STRATS = {x.replace("read_", ""): getattr(pd, x) for x in dir(pd) if x.startswith("read_")}
DEF_ST = tuple(sorted(STRATS))


def try_read(ifh, strats=DEF_ST):
    br = BufWrapper(ifh)
    for st in strats:
        if f := STRATS.get(st):
            try:
                return f(br)
            except:
                br.reset()


def try_readz(input_fhs, strats=DEF_ST):
    for x in inputs:
        y = try_read(x)
        if y is not None:
            yield y


def main():
    parser = argparse.ArgumentParser(  # description='this program',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("input", nargs="*", default=[sys.stdin], type=argparse.FileType("r", encoding="utf-8"))
    parser.add_argument("-v", "--verbose", action="count", default=0, help="increase verbosity for each -v")
    parser.add_argument("--version", action="version", version=VERSION)

    args = parser.parse_args()
    args.dfz = list(try_readz(args.input))

    print(args)
