import os
import pandas as pd
from collections import namedtuple


class File(namedtuple("File", ["fname", "df"])):
    def __repr__(self):
        return f"File<{os.path.basename(self.fname)}[{len(self.df)}]>"


def special_list_sort(*args):
    """generate a sorting function that prepends a score to the sort items"""

    def inner(x):
        score = 99
        for i, item in enumerate(args):
            if x == item or x in item:
                score = i
                break
        return f"{score:02d}{x}"

    return inner


def read_csv(fname, headers=None):
    if headers is None:
        df = pd.read_csv(fname)
    else:
        if isinstance(headers, pd.DataFrame):
            headers = df.columns.tolist()
        elif isinstance(headers, File):
            headers = headers.df.columns.tolist()
        df = pd.read_csv(fname, header=None, names=headers)
    return File(fname, df)
