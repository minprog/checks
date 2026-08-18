import re

import check50
import check50.c

# A binary search looks at about log2(n) of the n positions, so in an unsorted
# array it can only stumble upon a handful of the values that are in there. A
# search that walks the whole array finds all of them.
SEARCH_N = 2048
SEARCH_MAX_UNSORTED_HITS = SEARCH_N // 16

# A counting sort's work follows the range of the values, not how many there
# are, so sorting two numbers 0 and 65535 costs it about as much as sorting
# thousands. For a sort that compares numbers with each other, sorting two of
# them is practically free.
SORT_MIN_RATIO = 0.02


def _number(output, key):
    """Read one "KEY value" line from the output of a test program"""
    match = re.search(rf"^{key}\s+(-?\d+)\s*$", output, re.MULTILINE)

    if match is None:
        raise check50.Failure(
            f"could not read the output of the test program (missing {key})",
            help="The check compiled your helpers.c with a main of its own that "
                 "calls your function directly. That program did not print "
                 "what was expected, which usually means it crashed. Check for "
                 "reading or writing outside of the array.\n"
                 f"Output was:\n{output}")

    return int(match.group(1))


@check50.check()
def exists():
    """helpers.c exists."""
    check50.exists("helpers.c")


@check50.check(exists)
def compiles():
    """helpers.c compiles."""
    check50.include("helpers.h", "find.c", "wrong.c", "search_main.c", "sort_main.c")
    check50.c.compile("find.c", "helpers.c", exe_name="find", lcs50=True)
    check50.c.compile("wrong.c", "helpers.c", exe_name="wrong", lcs50=True)


@check50.check(compiles)
def finds_42_in_50():
    """finds 42 in 50 sorted numbers"""
    check50.run("./find 42 -s 50").stdout("Found needle in haystack")


@check50.check(compiles)
def finds_28_in_100():
    """finds 28 in 100 sorted numbers"""
    check50.run("./find 28 -s 100").stdout("Found needle in haystack")


@check50.check(compiles)
def not_find_42_in_30():
    """does not find 42 in 30 sorted numbers"""
    check50.run("./find 42 -s 30").stdout("Didn't find needle in haystack")


@check50.check(compiles)
def finds_0_in_5():
    """finds 0 in 5 sorted numbers"""
    check50.run("./find 0 -s 5").stdout("Found needle in haystack")


@check50.check(compiles)
def wrong_find():
    """search() returns false for non-positive n"""
    check50.run("./wrong").exit(0)


@check50.check(compiles)
def search_is_binary_search():
    """search() is implemented as Binary Search"""
    check50.c.compile("search_main.c", "helpers.c", exe_name="search_test", lcs50=True)

    process = check50.run("./search_test")
    output = process.stdout(timeout=30)

    if process.exitcode != 0:
        raise check50.Failure(
            "the test program did not finish properly",
            help="The check compiled your helpers.c with a main of its own "
                 "that calls your function directly, and that program "
                 f"stopped with an error (exit code {process.exitcode}). A "
                 "crash here usually means reading or writing outside of the "
                 f"array.\nOutput was:\n{output}")

    n = _number(output, "N")
    sorted_hits = _number(output, "SORTED_HITS")
    unsorted_hits = _number(output, "UNSORTED_HITS")

    if sorted_hits != n:
        raise check50.Failure(
            f"your search found only {sorted_hits} of {n} values that were "
            f"in a sorted array",
            help=f"The check filled an array with the numbers 0 up to "
                 f"{n - 1}, in order, and then searched for every single "
                 f"one of them. Your search should find all {n}. Before it "
                 f"can be decided whether your search is a Binary Search, "
                 f"it has to find values that are actually there.")

    if unsorted_hits > SEARCH_MAX_UNSORTED_HITS:
        raise check50.Failure(
            f"your search does not look like a Binary Search: it found "
            f"{unsorted_hits} of {n} values in an >>unsorted<< array. Binary search should "
            f"rarely find values in an unsorted array, because it only looks at a handful of "
            f"the positions")


@check50.check(compiles)
def sort_is_counting_sort():
    """sort() is implemented as Counting Sort"""
    check50.c.compile("sort_main.c", "helpers.c", exe_name="sort_test", lcs50=True)

    process = check50.run("./sort_test")
    output = process.stdout(timeout=90)

    if process.exitcode != 0:
        raise check50.Failure(
            "the test program did not finish properly",
            help="The check compiled your helpers.c with a main of its own "
                 "that calls your function directly, and that program "
                 f"stopped with an error (exit code {process.exitcode}). A "
                 "crash here usually means reading or writing outside of the "
                 f"array.\nOutput was:\n{output}")

    tiny_ok = _number(output, "TINY_OK")
    big_ok = _number(output, "BIG_OK")
    tiny_reps = _number(output, "TINY_REPS")
    tiny_us = _number(output, "TINY_US")
    big_reps = _number(output, "BIG_REPS")
    big_us = _number(output, "BIG_US")

    # Timing a sort that does not sort says nothing about the algorithm
    if not tiny_ok or not big_ok:
        which = "2 numbers" if not tiny_ok else "8000 numbers"
        raise check50.Failure(
            f"your sort did not correctly sort {which}",
            help="Before the check can time your sort, it makes sure that "
                 "it sorts at all. It sorted the numbers 65535 and 0, and "
                 "8000 random numbers, and checked that the result runs "
                 "from small to large and still holds exactly the same "
                 "numbers. That did not work out, so nothing can be said "
                 "about which algorithm you used yet. Get the sorting "
                 "itself right first.")

    if tiny_reps == 0 or big_reps == 0 or big_us <= 0:
        raise check50.Failure(
            "could not measure how long your sort takes",
            help="The check tried to time your sort but got no usable "
                 "measurement out of it.")

    tiny_per_call = tiny_us / tiny_reps
    big_per_call = big_us / big_reps
    ratio = tiny_per_call / big_per_call

    check50.data(tiny_per_call=tiny_per_call, big_per_call=big_per_call, ratio=ratio)

    if ratio < SORT_MIN_RATIO:
        raise check50.Failure(
            f"your sort does not look like a Counting Sort: sorting 2 "
            f"numbers costs {tiny_per_call:.1f} microseconds and sorting "
            f"8000 numbers {big_per_call:.1f}, a ratio of {ratio:.5f} "
            f"where at least {SORT_MIN_RATIO} was expected",
            help=f"How long a Counting Sort takes depends on the range of "
                 f"the numbers, not on how many there are: it walks past "
                 f"every possible value. Sorting just the two numbers 0 "
                 f"and 65535 therefore costs it about as much as sorting "
                 f"8000 numbers, so the ratio comes out near 1. A sorting "
                 f"algorithm that compares numbers with each other "
                 f"(insertion, selection, bubble, quick) has almost "
                 f"nothing to do with only two numbers, which gives a "
                 f"ratio far below {SORT_MIN_RATIO}.")
