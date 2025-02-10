import check50
import check50.c
import check50.internal
import contextlib
import os
import sys
import re

@check50.check()
def exists():
    """goldbach.c exists"""
    check50.exists("goldbach.c")

@check50.check(exists)
def compiles():
    """goldbach.c compiles"""
    check50.c.compile("goldbach.c", lcs50=True)

@check50.check(compiles)
def test_output():
    """handles printing the right numbers in the right format (we think)"""
    with logged_check_factory("./goldbach") as create_check:
        out = create_check().stdout(timeout=20)
    lines = [line.strip() for line in out.split("\n") if line.strip()]

    primes = set([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997])

    all_expected_even_numbers = set(range(2, 1001, 2))
    remaining_expected_even_numbers = set(range(2, 1001, 2))

    for line in lines:
        elems = line.split(" ")

        if len(elems) != 5:
            raise check50.Failure(f"Expected each line to be of the format: a = b + c, but found '{line}'")

        try:
            a, b, c = int(elems[0]), int(elems[2]), int(elems[4])
        except ValueError:
            raise check50.Failure(f"Expected each line to be of the format: a = b + c, but found '{line}'")

        if a != b + c:
            raise check50.Failure(f"Expected the sum of the right two parts to be equal to the left part, but found '{line}'")

        if b not in primes:
            raise check50.Failure(f"{b} is not a prime number in '{line}'")

        if c not in prime:
            raise check50.Failure(f"{c} is not a prime number in '{line}'")

        if a % 2 != 0:
            raise check50.Failure(f"{a} is not an even number in '{line}'")

        if a not in all_expected_even_numbers:
            raise check50.Failure(f"{a} is not an even number up to and including 1000 in '{line}'")

        if a not in remaining_expected_even_numbers:
            raise check50.Failure(f"{a} is printed twice, second time on line: '{line}'")

        remaining_expected_even_numbers.remove(a)

    if remaining_expected_even_numbers:
        raise check50.Failure(f"Missed equations for the following even numbers: {remaining_expected_even_numbers}")

# helpers --------------------------------------------------------------------

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
def logged_check_factory(command):
    """
    A factory of checks that logs everything on stdin/stdout.
    The log is written to the data.output field of check50's json output.
    """
    stream = Stream()

    def create_check():
        check = check50.run(command)
        check.process.logfile = stream
        return check

    try:
        yield create_check
    finally:
        check50.data(output=stream.text)
