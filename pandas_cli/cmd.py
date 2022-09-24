#!/usr/bin/env python
# coding: utf-8

import sys
import argparse
import pandas as pd
import logging
from .version import __version__ as VERSION
from .magic_buffer import MagicBuffer

STRATS = {x.replace("read_", ""): getattr(pd, x) for x in dir(pd) if x.startswith("read_")}
NOGO_ST = ("clipboard",)
DEF_ST = tuple(x for x in sorted(STRATS) if x not in NOGO_ST)

log = logging.getLogger(__name__)


def try_read(ifh, strats=DEF_ST):
    br = MagicBuffer(ifh)
    for st in strats:
        if f := STRATS.get(st):
            try:
                return f(br)
            except Exception as e:
                log.debug("strategy=%s did not work for reading %s: %s", st, ifh, e)
                br.reset()
    log.warning("could not find a way to read %s", ifh)


def try_readz(ifhs, strats=DEF_ST):
    for fh in ifhs:
        dat = try_read(fh)
        if dat is not None:
            yield dat


def main():
    parser = argparse.ArgumentParser(  # description='this program',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("input", nargs="*", default=[sys.stdin], type=argparse.FileType("r", encoding="utf-8"))
    parser.add_argument("-v", "--verbose", action="count", default=0, help="increase verbosity for each -v")
    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument(
        "-s",
        "--strats",
        "--input-strategies",
        type=str,
        action="append",
        help="decode strategies to try on the different inputs",
        default=DEF_ST,
    )

    args = parser.parse_args()

    if args.verbose >= 2:
        level = logging.DEBUG
    elif args.verbose >= 1:
        level = logging.INFO
    else:
        level = logging.ERROR

    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="%(asctime)s %(name)s [%(process)d] %(levelname)s: %(message)s",
    )

    args.dfz = list(try_readz(args.input))

    print(args)
