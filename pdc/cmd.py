#!/usr/bin/env python
# coding: utf-8

import argparse
import subprocess
import pdc.util

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
        type=pdc.util.read_csv,
        help="csv input files",
    )

    parser.add_argument('--headers-from', type=pdc.util.FILE_CACHE.set_headers_from, help="use the headers from this file to populate the column names in --csv-nh")

    parser.add_argument(
        "--csv-nh",
        "--csv-sans-header",
        "--csv-no-header",
        "-d",
        action="extend",
        dest="files",
        metavar="FILE",
        nargs="+",
        type=pdc.util.read_csv_nh,
        help="will use headers from whichever --csv was loaded last or the file specified with --headers-from to populate the column_names"
    )

    args = parser.parse_args(a, **kw)

    return args
