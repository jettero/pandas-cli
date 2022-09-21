#!/usr/bin/env python
# coding: utf-8

import os, sys
import argparse
import random
import simplejson as json

parser = argparse.ArgumentParser()
parser.add_argument("-b", "--objects", type=int, default=int(os.environ.get("LINES", 25))-5)
parser.add_argument("-a", "--attribute", action='append', type=str);
parser.add_argument("-p", "--precision", type=int, default=4);

args = parser.parse_args()
attr = args.attribute or ('one', 'two', 'three')

l = list({
        x: float(f'{i + 0.5 + 0.5*random.random():0.{args.precision}f}') for i,x in enumerate(attr)
    } for _ in range(args.objects))

json.dump(l, sys.stdout, sort_keys=True, indent=2)
