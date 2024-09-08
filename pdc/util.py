import os
import sys
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


ID_COUNTER = 1


def read_csv(fname, headers=None, id=None):
    global ID_COUNTER
    if id is None or int(id) < 1:
        id = ID_COUNTER
        ID_COUNTER += 1
    else:
        if id >= ID_COUNTER:
            ID_COUNTER = id + 1
    if headers is None:
        df = pd.read_csv(fname)
    else:
        if isinstance(headers, pd.DataFrame):
            headers = df.columns.tolist()
        elif isinstance(headers, File):
            headers = headers.df.columns.tolist()
        df = pd.read_csv(fname, header=None, names=headers)
    return File(id, fname, df)


SAY_DEBUG = 0
SAY_INFO = 1
SAY_WARN = 2
SAY_ERROR = 3
SAY_WORDS = "DEBUG INFO WARN ERROR".split()


def set_say_level(x=None):
    global SAY_LEVEL
    try:
        x = x if x is not None else os.environ["PDC_LOG_LEVEL"]
        try:
            x = x.upper()
            x = SAY_WORDS.index(x)
        except (ValueError, AttributeError):
            x = int(x)
        SAY_LEVEL = max(SAY_DEBUG, min(x, SAY_ERROR))
    except (KeyError, ValueError):
        SAY_LEVEL = SAY_ERROR
    return SAY_LEVEL


set_say_level()


def say(*msg, level=SAY_INFO):
    level = max(SAY_DEBUG, min(level, SAY_ERROR))
    if level >= SAY_LEVEL:
        print(f"[{SAY_WORDS[level]}]", *msg, file=sys.stderr)


def say_debug(*msg):
    say(*msg, level=SAY_DEBUG)


def say_info(*msg):
    say(*msg, level=SAY_INFO)


def say_warn(*msg):
    say(*msg, level=SAY_WARN)


say_warning = say_warn


def say_error(*msg):
    say(*msg, level=SAY_ERROR)
