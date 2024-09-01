#!/usr/bin/env python
# coding: utf-8

import os, sys
import argparse
import random
import simplejson as json


def main(*margs):
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--rows", type=int, default=-1)
    parser.add_argument("-a", "--attribute", action="append", type=str)
    parser.add_argument("-p", "--precision", type=int, default=4)
    parser.add_argument("-o", "--output-file", type=argparse.FileType("w"), default=sys.stdout)

    if margs:
        args = parser.parse_args(margs)
    else:
        args = parser.parse_args()

    attr = args.attribute or ("one", "two", "three")

    if args.rows < 1:
        args.rows = int((int(os.environ.get("LINES", 25)) - 5) / 5)

    l = list(
        {x: float(f"{(i+1) + 0.5 + 0.5*random.random():0.{args.precision}f}") for i, x in enumerate(attr)}
        for _ in range(args.rows)
    )

    json.dump(l, args.output_file, sort_keys=True, indent=2)
    print("", file=args.output_file)


if __name__ == "__main__":
    main()
