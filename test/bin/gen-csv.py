#!/usr/bin/env python

import os
import argparse
import random

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--rows", type=int, default=int(os.environ.get("LINES", 25)) - 5)
parser.add_argument("-c", "--column", action="append", type=str)
parser.add_argument("-p", "--precision", type=int, default=4)

args = parser.parse_args()

headers = args.column or ("one", "two", "three")

print(",".join(headers))
for _ in range(args.rows):
    l = [f"{(j+1) + 0.5 + 0.5*random.random():0.{args.precision}f}" for j, v in enumerate(headers)]
    print(",".join(l))
