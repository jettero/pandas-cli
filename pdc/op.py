#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from .util import File


def concat(*df):
    return pd.concat([x.df if isinstance(x, File) else x for x in df])
