#!/usr/bin/env python
# coding: utf-8


class MagicBuffer:
    """try to allow reading ahead on buffers that may not support seeking"""

    def __init__(self, already_buffered_filehandle_maybe):
        self.fh = already_buffered_filehandle_maybe

    def __repr__(self):
        return f"MagicBuffer<name={ self.fh.name }>"

    def head(self):
        if hasattr(self, "_head"):
            return self._head
        self.reset()
        self._head = self.fh.read(128)
        self.reset()
        return self._head

    def __str__(self):
        return self.head()

    def reset(self):
        self.fh.seek(0, 0)

    def __getattr__(self, aname):
        if not aname.startswith("_"):
            try:
                a = getattr(self.fh, aname)
                setattr(self, aname, a)
                return a
            except AttributeError:
                pass
        raise AttributeError(f"'{self!r}' has no attribute '{aname}'")
