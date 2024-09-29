#!/usr/bin/env python
# coding: utf-8

import sys
import argparse
import subprocess
import tabulate
import pdc.util
import pdc.parser

try:  # pragma: no cover
    from pdc.version import version as scm_version
except ModuleNotFoundError:  # pragma: no cover
    scm_version = "¿unknown?"

VERSION = scm_version.split("+")[0]


def populate_args(*a, **kw):  # pragma: no cover
    parser = argparse.ArgumentParser(prog="pd-thing", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "-V", "--version", action="version", version=VERSION, help=f"show version ({VERSION}) and exit"
    )

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

    parser.add_argument(
        "--headers-from",
        type=pdc.util.FILE_CACHE.set_headers_from,
        help="use the headers from this file to populate the column names in --csv-nh",
    )

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
        help="will use headers from whichever --csv was loaded last or "
        "the file specified with --headers-from to populate the column_names",
    )

    parser.add_argument("-o", "--output", help="output filename", default="-")

    OUTPUT_FORMATS = ["csv", "tsv", "xls", *(f":{x}" for x in tabulate.tabulate_formats)]
    parser.add_argument(
        "-f",
        "--output-format",
        choices=OUTPUT_FORMATS,
        metavar="FMT",
        help='output format (default: ":orgtbl"): '
        "csv/tsv/xls attempt to use pd.DataFrame output formats. "
        "Formats starting with ':' are assumed to be tabulate format names. "
        f"The full list includes: {', '.join(OUTPUT_FORMATS)}",
    )

    parser.add_argument(
        "--max-output-table-lines",
        "--max-lines",
        "-m",
        type=int,
        default=15,
        help="in tabulate mode, show only this many lines",
    )

    parser.add_argument(
        "-s",
        "--show-each-file",
        action="store_true",
        default=False,
        help="in tabulate mode, show each input file as a table",
    )

    parser.add_argument(
        "-a", "--action", default="f*: a + b", type=str, help="the operations and aggregations you wish to run"
    )

    ##########################################################
    args_for_parse_args = list()
    if a:
        args_for_parse_args.append(a)

    args = parser.parse_args(*args_for_parse_args)

    if args.output_format is None:
        if args.output is not None:
            pass  # TODO: if we didn't specify a format, then we could maybe dig it out of the output filename if given
        args.output_format = ":orgtbl"

    return args


def output(args, df):  # pragma: no cover
    if args.output is None:
        ofh = sys.stdout

    if args.output_format.startswith(":"):
        fmt = args.output_format[1:]

    print("actually outputting things is a TODO item")


def entry_point(*a, **kw):  # pragma: no cover
    args = populate_args(*a, **kw)

    pf = pdc.parser.parse(args.action, files=args.files)
    df = pf()

    output(args, df)
