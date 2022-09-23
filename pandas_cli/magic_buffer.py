#!/usr/bin/env python
# coding: utf-8


class MagicBuffer:
    """try to allow reading ahead on buffers that may not support seeking"""

    def __init__(self, already_buffered_filehandle_maybe):
        self.fh = already_buffered_filehandle_maybe

    def reset(self):
        self.fh.seek(0, 0)
