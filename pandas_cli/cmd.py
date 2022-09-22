#!/usr/bin/env python
# coding: utf-8

import sys
import argparse
import pandas as pd
from .version import __version__ as VERSION

def main():
    parser = argparse.ArgumentParser(  # description='this program',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("input", nargs="*", default=[sys.stdin], type=argparse.FileType('r', encoding='utf-8'))
    parser.add_argument("-v", "--verbose", action="count", default=0, help='increase verbosity for each -v')
    parser.add_argument("--version", action="version", version=VERSION)

    args = parser.parse_args()


    print(args)
