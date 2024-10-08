#!/usr/bin/env python
# coding: utf-8

import os
import sys
import argparse
import subprocess
import tabulate
import pandas as pd
import pdc.util
import pdc.parser

try:  # pragma: no cover
    from pdc.version import version as scm_version
except ModuleNotFoundError:  # pragma: no cover
    scm_version = "¿unknown?"

VERSION = scm_version.split("+")[0]

ARG_PARSER = None


def output(args, file, describe_as=None):  # pragma: no cover
    if args.output is None:
        ofh = sys.stdout

    if args.output_format.startswith(":"):
        fmt = args.output_format[1:]
        if args.max_output_table_lines > 0 and len(file.df) > args.max_output_table_lines:
            ellipis_row = pd.DataFrame([{col: "⋮" for col in file.columns}])
            df = pd.concat((file.df.head(args.max_output_table_lines), ellipis_row), ignore_index=True)
        if describe_as:
            say_info(f"\n-----=: {describe_as}")

        kw = dict(tablefmt=fmt, showindex=False)
        if file.flags.get("transposed", False):
            kw["showindex"] = True
        else:
            kw["headers"] = file.columns
        print(tabulate.tabulate(file.df, **kw))
        return

    # if args.output_format == 'csv':

    say_error("actually outputting things is a TODO item")


def populate_args(*a, **kw):  # pragma: no cover
    global ARG_PARSER
    ARG_PARSER = parser = argparse.ArgumentParser(
        prog="pd-thing", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-V", "--version", action="version", version=VERSION, help=f"show version ({VERSION}) and exit"
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
        f"The full list of table is: {', '.join(OUTPUT_FORMATS)}",
    )

    def _compute_sensible_default():
        try:
            rows = int(os.environ.get("LINES", 25))
        except:
            rows = 25
        rows = int(0.75 * rows)
        if rows < 1:
            return 1
        return rows

    parser.add_argument(
        "--max-output-table-lines",
        "--max-lines",
        "-m",
        type=int,
        default=_compute_sensible_default(),
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
    parser.add_argument(
        "files",
        action="extend",
        metavar="FILE",
        nargs="*",
        type=pdc.util.read_file,
        help="""input files have some magic conventions. The file extension is
        used to determine the type of file, but if the filename ends with @csv
        (or @json, @xls, @tsv, etc); then the actual extension will be ignored
        in favor of this descriptor. Also, some csv files lack a header line.
        To mark a file as one lacking headers, start the filename with a colon
        ':' -- %(prog)s will attempt to use the column/header names from which
        ever file was loaded before this one. And to specify a specific source
        for such headers, simply specify the source before the colon leader. To
        specify files that happen to contain colons ':' or atperands '@',
        escape them with backslashes. Backslashes themselves can be escaped
        with more backslashes.
        """,
    )

    parser.add_argument("--verbose", "-v", action="count", default=0)

    ##########################################################
    # Iff we have args in 'a', format them as a single list arg for parse_args.
    # Also, we will not provide such a list at all if 'a' is empty as this
    # confuses parse_args.
    args_for_parse_args = list()
    if a:
        args_for_parse_args.append(a)
    args = parser.parse_args(*args_for_parse_args)
    ##########################################################

    if args.verbose:
        pdc.util.set_say_level(-args.verbose)

    if args.output_format is None:
        if args.output is not None:
            # TODO: if we didn't specify a format, then we could maybe dig it
            # out of the output filename if given
            pass
        args.output_format = ":orgtbl"

    return args


def entry_point(*a, **kw):  # pragma: no cover
    phase = "reticulating splines"
    pdc.util.FILE_CACHE.clear()
    try:
        phase = "processing arguments and options"
        args = populate_args(*a, **kw)

        if not args.files:
            ARG_PARSER.print_help()
            sys.exit(0)

        phase = "parsing action"
        pf = pdc.parser.parse(args.action, files=args.files)

        phase = "completing action"
        df = pf()

        phase = "outputting result"
        output(args, df)
    except Exception as error:
        pdc.util.say_error(f"while {phase}:\n\t{error!r}")
