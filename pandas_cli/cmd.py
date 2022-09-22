#!/usr/bin/env python
# coding: utf-8

import click

from .version import __version__ as VERSION

@click.command()
@click.version_option(version=VERSION)
def main():
    pass
