#!/usr/bin/env python
# coding: utf-8

import argparse
import subprocess
from .util import read_csv


def populate_args(*a, **kw):
    parser = argparse.ArgumentParser(prog="pd-thing", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-V", "--version", action="store_true", help="show version and exit")

    parser.add_argument(
        "--csv",
        "-c",
        action="extend",
        dest="files",
        metavar="FILE",
        nargs="+",
        type=read_csv,
        help="csv input files",
    )

    args = parser.parse_args(a, **kw)

    return args
