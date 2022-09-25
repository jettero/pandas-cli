#!/usr/bin/env python
# coding: utf-8

import re
import sys
import argparse
import pandas as pd
import logging
from .version import __version__ as VERSION
from .util import special_list_sort as sls

STRATS = {x.replace("read_", ""): getattr(pd, x) for x in dir(pd) if x.startswith("read_")}
NOGO_ST = ("clipboard",)
MY_SORT = (("csv", "json"), ("table", "excel", "pickle"))
DEF_ST = tuple(x for x in sorted(STRATS, key=sls(*MY_SORT)) if x not in NOGO_ST)

log = logging.getLogger(__name__)


def try_read(ifh, strats=DEF_ST):
    try:
        ifh_name = ifh.name
    except:
        ifh_name = type(n)

    try:
        p = ifh.peek(128)[:128]
        log.debug("peek() in %s: %r", ifh_name, p)
    except AttributeError:
        p = ifh.buffer.peek(128)[:128]
        log.debug("buf.peek() in %s: %r", ifh_name, p)
    except:
        p = ""  # I guess we can't peek()
        log.debug("we can't peak in %s: %r", ifh_name, p)

    # if the ifh isn't seekable (e.g., stdin); then we only get one try
    # so we better try to pre-guess our guesses
    if p:
        if re.search(rb'^[{[\s]+"[^"]+":', p, flags=re.DOTALL):
            strats = list(sorted(strats, key=sls("json", *MY_SORT)))

    for st in strats:
        if f := STRATS.get(st):
            try:
                r = f(ifh)
                log.info("parsed %s with strategy=%s", ifh_name, st)
                return r
            except Exception as e:
                if not ifh.seekable():
                    break
                log.debug("strategy=%s did not work for reading %s: %s", st, ifh_name, e)
                ifh.seek(0)

    log.warning("could not find a way to read %s", ifh_name)


def try_readz(ifhs, strats=DEF_ST):
    for fh in ifhs:
        dat = try_read(fh)
        if dat is not None:
            yield dat


def main():
    parser = argparse.ArgumentParser(  # description='this program',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("input", nargs="*", default=[sys.stdin], type=argparse.FileType("rb"))
    parser.add_argument("-v", "--verbose", action="count", default=0, help="increase verbosity for each -v")
    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument("-o", "--output-filename", type=str)
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

    if args.verbose >= 3:
        level = logging.DEBUG
    elif args.verbose >= 2:
        level = logging.INFO
    elif args.verbose >= 1:
        level = logging.WARNING
    else:
        level = logging.ERROR

    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="%(asctime)s %(name)s [%(process)d] %(levelname)s: %(message)s",
    )

    args.dfz = list(try_readz(args.input))
