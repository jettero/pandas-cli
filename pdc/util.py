import os
import pandas as pd
from collections import namedtuple


class File(namedtuple("File", ["id", "fname", "df"])):
    def __repr__(self):
        return f"f{self.id}<{os.path.basename(self.fname)}>"


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


GLOBAL_ID_COUNTER = 1


def read_csv(fname, headers=None, id=None):
    global GLOBAL_ID_COUNTER
    if id is None or int(id) < 1:
        id = GLOBAL_ID_COUNTER
        GLOBAL_ID_COUNTER += 1
    else:
        if id >= GLOBAL_ID_COUNTER:
            GLOBAL_ID_COUNTER = id + 1
    if headers is None:
        df = pd.read_csv(fname)
    else:
        if isinstance(headers, pd.DataFrame):
            headers = df.columns.tolist()
        elif isinstance(headers, File):
            headers = headers.df.columns.tolist()
        df = pd.read_csv(fname, header=None, names=headers)
    return File(id, fname, df)
