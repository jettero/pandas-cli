import os
import sys
import pandas as pd
from collections import namedtuple


class File(namedtuple("File", ["fname", "df"])):
    def __repr__(self):
        return f"<{os.path.basename(self.fname)}>"


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


SAY_TRACE = 0
SAY_DEBUG = SAY_TRACE + 1
SAY_INFO = SAY_DEBUG + 1
SAY_WARN = SAY_INFO + 1
SAY_ERROR = SAY_WARN + 1
SAY_WORDS = "TRACE DEBUG INFO WARN ERROR".split()


def set_say_level(x=None):
    global SAY_LEVEL
    try:
        x = x if x is not None else os.environ["PDC_SAY_LEVEL"]
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


SAY_TRIGGER = bytes([87, 84, 70]).decode()


def say(*msg, level=SAY_INFO):
    level = max(SAY_TRACE, min(level, SAY_ERROR))
    if level >= SAY_LEVEL or any(SAY_TRIGGER in s for s in msg):
        print(f"[{SAY_WORDS[level]}]", *msg, file=sys.stderr)


def say_trace(*msg):
    say(*msg, level=SAY_TRACE)


def say_debug(*msg):
    say(*msg, level=SAY_DEBUG)


def say_info(*msg):
    say(*msg, level=SAY_INFO)


def say_warn(*msg):
    say(*msg, level=SAY_WARN)


say_warning = say_warn


def say_error(*msg):
    say(*msg, level=SAY_ERROR)
