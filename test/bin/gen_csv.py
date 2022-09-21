#!/usr/bin/env python

import os, sys
import argparse
import random

def main(*margs):
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--rows", type=int, default=int(os.environ.get("LINES", 25)) - 5)
    parser.add_argument("-c", "--column", action="append", type=str)
    parser.add_argument("-p", "--precision", type=int, default=4)
    parser.add_argument('-o', '--output-file', type=argparse.FileType('w'), default=sys.stdout);

    if margs:
        args = parser.parse_args(margs)
    else:
        args = parser.parse_args()

    headers = args.column or ("one", "two", "three")

    print(",".join(headers), file=args.output_file)
    for _ in range(args.rows):
        l = [f"{(j+1) + 0.5 + 0.5*random.random():0.{args.precision}f}" for j, v in enumerate(headers)]
        print(",".join(l), file=args.output_file)

if __name__ == '__main__':
    main()
