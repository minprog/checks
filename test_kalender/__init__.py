import check50
import check50.c
import check50.internal
import contextlib
import os
import sys
import re
import glob
import subprocess

from collections import Counter

@check50.check()
def test_kalender():
    """runnen van tests voor kalender"""
    subprocess.run(["pip3", "install", "pytest"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with logged_check_factory("python3 -m pytest --color=no -v") as run_check:
        run_check().stdin('')

class Stream:
    """Stream-like object that stores everything it receives"""
    def __init__(self):
        self.entries = []

    @property
    def text(self):
        return "".join(self.entries)

    def write(self, entry):
        entry = entry.replace("\r\n", "\n").replace("\r", "\n")
        self.entries.append(entry)

    def flush(self):
        pass

    def reset(self):
        self.entries = []


@contextlib.contextmanager
def logged_check_factory(name):
    """
    A factory of checks that logs everything on stdin/stdout.
    The log is written to the data.output field of check50's json output.
    """
    command = name
    stream = Stream()

    def create_check(*args):
        x=list(args)
        x.insert(0,command)
        x = " ".join(x)
        check = check50.run(x)
        check.process.logfile = stream
        return check

    try:
        yield create_check
    finally:
        check50.data(output=stream.text)
