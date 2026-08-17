import re

import check50
import check50.c
import check50.internal

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../../helpers/helpers.py"
)

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
    """Read one "KEY value" line from the output of an injected main"""
    match = re.search(rf"^{key}\s+(-?\d+)\s*$", output, re.MULTILINE)

    if match is None:
        raise check50.Failure(
            f"could not read the output of the test program (missing {key})",
            help="The check compiled your find.c with a main of its own that "
                 "calls your function directly. That program did not print "
                 "what was expected, which usually means it crashed. Check for "
                 "reading or writing outside of the array.\n"
                 f"Output was:\n{output}")

    return int(match.group(1))


@check50.check()
def exists():
    """find.c exists."""
    check50.exists("find.c")

@check50.check(exists)
def compiles():
    """find.c compiles."""
    check50.c.compile("find.c", lcs50=True)

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


# Note: the two checks below replace the student's main with one of their own,
# so that they can call search() and sort() directly. helpers.replace_main only
# puts the original main back when a check fails, so both hang off compiles as
# siblings and nothing depends on them.

@check50.check(compiles)
def search_is_binary_search():
    """search() is implemented as Binary Search"""
    main = r"""
#include <stdio.h>

#define CHECK_N 2048

static unsigned int check_seed = 20260814u;

static unsigned int check_rand(void)
{
    check_seed = check_seed * 1103515245u + 12345u;
    return (check_seed >> 16) & 0x7fffu;
}

int main(void)
{
    static int master[CHECK_N];
    static int work[CHECK_N];

    // First an array that really is sorted: every value has to be found
    for (int i = 0; i < CHECK_N; i++)
    {
        master[i] = i;
    }

    int sorted_hits = 0;
    for (int value = 0; value < CHECK_N; value++)
    {
        // Hand over a fresh copy every time, so a search that changes the
        // array cannot make the next call easier
        for (int i = 0; i < CHECK_N; i++)
        {
            work[i] = master[i];
        }
        if (search(value, work, CHECK_N))
        {
            sorted_hits++;
        }
    }

    // Then the same values, shuffled
    for (int i = CHECK_N - 1; i > 0; i--)
    {
        int j = (int) (check_rand() % (unsigned int) (i + 1));
        int swap = master[i];
        master[i] = master[j];
        master[j] = swap;
    }

    int unsorted_hits = 0;
    for (int value = 0; value < CHECK_N; value++)
    {
        for (int i = 0; i < CHECK_N; i++)
        {
            work[i] = master[i];
        }
        if (search(value, work, CHECK_N))
        {
            unsorted_hits++;
        }
    }

    printf("N %d\n", CHECK_N);
    printf("SORTED_HITS %d\n", sorted_hits);
    printf("UNSORTED_HITS %d\n", unsorted_hits);
}
"""
    with helpers.replace_main("find.c", main, show_main_in_help=False):
        check50.c.compile("find.c", lcs50=True)

        process = check50.run("./find")
        output = process.stdout(timeout=30)

        if process.exitcode != 0:
            raise check50.Failure(
                "the test program did not finish properly",
                help="The check compiled your find.c with a main of its own "
                     "that calls your function directly, and that program "
                     "stopped with an error (exit code "
                     f"{process.exitcode}). A crash here usually means "
                     "reading or writing outside of the array.\n"
                     f"Output was:\n{output}")

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
    main = r"""
#include <stdio.h>
#include <sys/resource.h>

#define CHECK_BIG 8000
#define CHECK_FLOOR_US 50000L
#define CHECK_TINY_CAP 5000
#define CHECK_BIG_CAP 200

static unsigned int check_seed = 20260814u;

static unsigned int check_rand(void)
{
    check_seed = check_seed * 1103515245u + 12345u;
    return check_seed >> 8;
}

// Processor time used by this program, so that other work on the machine
// cannot influence the measurement
static long check_cpu_us(void)
{
    struct rusage usage;
    getrusage(RUSAGE_SELF, &usage);
    return (long) usage.ru_utime.tv_sec * 1000000L + (long) usage.ru_utime.tv_usec
         + (long) usage.ru_stime.tv_sec * 1000000L + (long) usage.ru_stime.tv_usec;
}

// Sorted, and still exactly the same numbers as before? The sum and the sum of
// squares do not depend on the order, so together they catch numbers that got
// lost, duplicated or invented.
static int check_sorted(int values[], int n, unsigned long long sum,
                        unsigned long long squares)
{
    unsigned long long total = 0;
    unsigned long long total_squares = 0;

    for (int i = 0; i < n; i++)
    {
        if (i > 0 && values[i - 1] > values[i])
        {
            return 0;
        }
        total += (unsigned long long) values[i];
        total_squares += (unsigned long long) values[i] * (unsigned long long) values[i];
    }

    return total == sum && total_squares == squares;
}

int main(void)
{
    // Two numbers, but as far apart as they can be: a counting sort has to walk
    // past every possible value in between, however few numbers there are
    static int tiny_master[2] = {65535, 0};
    static int tiny[2];
    static int big_master[CHECK_BIG];
    static int big[CHECK_BIG];

    unsigned long long tiny_sum = 0, tiny_squares = 0, big_sum = 0, big_squares = 0;

    for (int i = 0; i < 2; i++)
    {
        tiny_sum += (unsigned long long) tiny_master[i];
        tiny_squares += (unsigned long long) tiny_master[i] * (unsigned long long) tiny_master[i];
    }
    for (int i = 0; i < CHECK_BIG; i++)
    {
        big_master[i] = (int) (check_rand() % 65536u);
        big_sum += (unsigned long long) big_master[i];
        big_squares += (unsigned long long) big_master[i] * (unsigned long long) big_master[i];
    }

    // Keep sorting until enough time has been used to measure it reliably. An
    // expensive sort is over the floor after one go; a cheap one needs many.
    int tiny_ok = 1;
    long tiny_us = 0;
    int tiny_reps = 0;
    while (tiny_us < CHECK_FLOOR_US && tiny_reps < CHECK_TINY_CAP)
    {
        // Copying happens outside the measurement
        tiny[0] = tiny_master[0];
        tiny[1] = tiny_master[1];

        long started = check_cpu_us();
        sort(tiny, 2);
        tiny_us += check_cpu_us() - started;
        tiny_reps++;

        if (!check_sorted(tiny, 2, tiny_sum, tiny_squares))
        {
            tiny_ok = 0;
            break;
        }
    }

    int big_ok = 1;
    long big_us = 0;
    int big_reps = 0;
    while (big_us < CHECK_FLOOR_US && big_reps < CHECK_BIG_CAP)
    {
        // Also restore this one every time: an array that is already sorted is
        // much easier for some sorting algorithms
        for (int i = 0; i < CHECK_BIG; i++)
        {
            big[i] = big_master[i];
        }

        long started = check_cpu_us();
        sort(big, CHECK_BIG);
        big_us += check_cpu_us() - started;
        big_reps++;

        if (!check_sorted(big, CHECK_BIG, big_sum, big_squares))
        {
            big_ok = 0;
            break;
        }
    }

    printf("TINY_OK %d\n", tiny_ok);
    printf("BIG_OK %d\n", big_ok);
    printf("TINY_REPS %d\n", tiny_reps);
    printf("TINY_US %ld\n", tiny_us);
    printf("BIG_REPS %d\n", big_reps);
    printf("BIG_US %ld\n", big_us);
}
"""
    with helpers.replace_main("find.c", main, show_main_in_help=False):
        check50.c.compile("find.c", lcs50=True)

        process = check50.run("./find")
        output = process.stdout(timeout=90)

        if process.exitcode != 0:
            raise check50.Failure(
                "the test program did not finish properly",
                help="The check compiled your find.c with a main of its own "
                     "that calls your function directly, and that program "
                     "stopped with an error (exit code "
                     f"{process.exitcode}). A crash here usually means "
                     "reading or writing outside of the array.\n"
                     f"Output was:\n{output}")

        tiny_ok = _number(output, "TINY_OK")
        big_ok = _number(output, "BIG_OK")
        tiny_reps = _number(output, "TINY_REPS")
        tiny_us = _number(output, "TINY_US")
        big_reps = _number(output, "BIG_REPS")
        big_us = _number(output, "BIG_US")

        # Timing a sort that does not sort says nothing about the algorithm
        if not tiny_ok or not big_ok:
            which = "2 numbers" if not tiny_ok else f"{8000} numbers"
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

        check50.data(tiny_per_call=tiny_per_call, big_per_call=big_per_call,
                     ratio=ratio)

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
