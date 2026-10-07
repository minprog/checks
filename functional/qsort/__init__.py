"""Checks for the qsort assignment.

The student writes qsort.c (swap, qsort_) and compare.c (seven comparators).
sorter.c, the headers, the Makefile and data/ next to this file are copies of
the distribution the students get (programmeren-1/problems/functional/qsort/dist).

Three groups of checks, which are independent of each other on purpose, so that
students can work on them in any order:

* the comparators, tested with a test program of our own (no qsort_ involved)
* swap and qsort_, tested with comparators of our own (no compare.c involved)
* the whole program: ./sorter with the student's qsort_ and comparators, which
  verifies its own output
"""

import os
import re

import check50
import check50.c
import check50.internal

common = check50.internal.import_file(
    "common",
    check50.internal.check_dir / "../_common.py"
)

# qsort_ has to stay well below n^2 comparisons: n log2(n) is about 14 * n for
# these sizes. A good quicksort needs about 1.4 times that.
MAX_COMPARES_PER_N_LOG_N = 8

# Types the test programs use. Same as compare.h, but without needing it.
SIZES = r"""
#include <limits.h>
#include <math.h>
#include "qsort.h"
#include "compare.h"

#define SIGN(x) ((x) < 0 ? -1 : (x) > 0 ? 1 : 0)
"""


def harness(name, source, student_files, *, asan=True, timeout=5):
    """Compile a test program of our own with some of the student's files, run it, judge its output"""
    # every check runs in a fresh copy of the submission, which has no headers if the student did not hand them in
    for header in ["qsort.h", "compare.h"]:
        if not os.path.exists(header):
            check50.include(header)

    test = f"test_{name}.c"
    with open(test, "w") as f:
        f.write(common.PRELUDE + SIZES + source)

    flags = {"fsanitize": "address"} if asan and common.asan_works() else {}
    check50.c.compile(test, *student_files, exe_name=f"test_{name}", **flags)

    process = check50.run(f"./test_{name}", env={"ASAN_OPTIONS": "detect_leaks=0"})
    output = process.stdout(timeout=timeout)
    common._judge(student_files[0], output, process.exitcode)


def read(filename):
    with open(filename) as f:
        return f.read()


# ---------------------------------------------------------------- setup

@check50.check()
def exists():
    """qsort.c and compare.c exist"""
    check50.exists("qsort.c", "compare.c")


@check50.check(exists)
def compiles():
    """sorter compiles"""
    check50.include("sorter.c", "data")
    for filename in ["Makefile", "qsort.h", "compare.h"]:
        if not os.path.exists(filename):
            check50.include(filename)
    check50.run("make").exit(0)


@check50.check(exists)
def no_stdlib_qsort():
    """qsort_ does not use the qsort of the standard library"""
    source = read("qsort.c")
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    source = re.sub(r"//[^\n]*", "", source)
    if re.search(r"\bqsort\s*\(", source):
        raise check50.Failure("qsort.c calls qsort of the standard library",
                              help="You have to write qsort_ yourself, with a sorting algorithm of your own.")


# ---------------------------------------------------------------- comparators

@check50.check(exists)
def compare_int():
    """compare_int orders ints from small to large"""
    harness("compare_int", r"""
static void t_check(int x, int y, int want)
{
    int got = SIGN(compare_int(&x, &y));
    EXPECT(got == want, "compare_int(%d, %d) has the sign %d, expected %d", x, y, got, want);
}
int main(void)
{
    t_check(1, 2, -1);
    t_check(2, 1, 1);
    t_check(5, 5, 0);
    t_check(-3, 3, -1);
    t_check(-5, -9, 1);
    t_check(INT_MAX, -1, 1);
    t_check(-1, INT_MAX, -1);
    t_check(INT_MIN, 1, -1);
    t_check(1, INT_MIN, 1);
}
""", ["compare.c"])


@check50.check(exists)
def compare_int_desc():
    """compare_int_desc orders ints from large to small"""
    harness("compare_int_desc", r"""
static void t_check(int x, int y, int want)
{
    int got = SIGN(compare_int_desc(&x, &y));
    EXPECT(got == want, "compare_int_desc(%d, %d) has the sign %d, expected %d", x, y, got, want);
}
int main(void)
{
    t_check(1, 2, 1);
    t_check(2, 1, -1);
    t_check(5, 5, 0);
    t_check(-3, 3, 1);
    t_check(-5, -9, -1);
    t_check(INT_MAX, -1, -1);
    t_check(-1, INT_MAX, 1);
    t_check(INT_MIN, 1, 1);
}
""", ["compare.c"])


@check50.check(exists)
def compare_string():
    """compare_string orders strings alphabetically, like strcmp"""
    harness("compare_string", r"""
static void t_check(char *x, char *y, int want)
{
    int got = SIGN(compare_string(&x, &y));
    EXPECT(got == want, "compare_string(\"%s\", \"%s\") has the sign %d, expected %d", x, y, got, want);
}
int main(void)
{
    char copy[] = "apple";
    t_check("apple", "banana", -1);
    t_check("banana", "apple", 1);
    t_check("apple", copy, 0);
    t_check("app", "apple", -1);
    t_check("apple", "app", 1);
    t_check("Zebra", "apple", -1);
}
""", ["compare.c"])


@check50.check(exists)
def compare_length():
    """compare_length orders strings by length, ties alphabetically"""
    harness("compare_length", r"""
static void t_check(char *x, char *y, int want)
{
    int got = SIGN(compare_length(&x, &y));
    EXPECT(got == want, "compare_length(\"%s\", \"%s\") has the sign %d, expected %d", x, y, got, want);
}
int main(void)
{
    char copy[] = "pear";
    t_check("fig", "apple", -1);
    t_check("apple", "fig", 1);
    t_check("zzz", "aaaa", -1);
    t_check("pear", "plum", -1);
    t_check("plum", "pear", 1);
    t_check("pear", copy, 0);
}
""", ["compare.c"])


COUNTRIES = r"""
static country t_country(const char *name, long population, long area)
{
    country c;
    memset(&c, 0, sizeof(c));
    strncpy(c.name, name, sizeof(c.name) - 1);
    c.population = population;
    c.area = area;
    return c;
}
"""


@check50.check(exists)
def compare_country_name():
    """compare_country_name orders countries alphabetically by name"""
    harness("compare_country_name", COUNTRIES + r"""
static void t_check(country x, country y, int want)
{
    int got = SIGN(compare_country_name(&x, &y));
    EXPECT(got == want, "compare_country_name(%s, %s) has the sign %d, expected %d", x.name, y.name, got, want);
}
int main(void)
{
    country belgium = t_country("Belgium", 11700000, 30528);
    country chile = t_country("Chile", 19600000, 756102);
    country chile2 = t_country("Chile", 1, 1);
    t_check(belgium, chile, -1);
    t_check(chile, belgium, 1);
    t_check(chile, chile2, 0);
}
""", ["compare.c"])


@check50.check(exists)
def compare_country_population():
    """compare_country_population puts the most populous country first"""
    harness("compare_country_population", COUNTRIES + r"""
static void t_check(country x, country y, int want)
{
    int got = SIGN(compare_country_population(&x, &y));
    EXPECT(got == want, "compare_country_population(%s, %s) has the sign %d, expected %d", x.name, y.name, got, want);
}
int main(void)
{
    country big = t_country("Big", 1428600000, 3287263);
    country small = t_country("Small", 36000, 2);
    country huge = t_country("Huge", 5000000000L, 100);
    country other = t_country("Other", 1000000000L, 100);
    country same = t_country("Same", 36000, 99);
    t_check(big, small, -1);
    t_check(small, big, 1);
    t_check(small, same, 0);
    t_check(huge, other, -1);
    t_check(other, huge, 1);
}
""", ["compare.c"])


@check50.check(exists)
def compare_country_density():
    """compare_country_density puts the most densely populated country first"""
    harness("compare_country_density", COUNTRIES + r"""
static void t_check(country x, country y, int want)
{
    int got = SIGN(compare_country_density(&x, &y));
    EXPECT(got == want, "compare_country_density(%s, %s) has the sign %d, expected %d", x.name, y.name, got, want);
}
int main(void)
{
    country dense = t_country("Dense", 18000, 1);
    country sparse = t_country("Sparse", 1000000, 1000);
    country a = t_country("A", 1000, 3);
    country b = t_country("B", 1001, 3);
    country twin1 = t_country("Twin1", 100, 4);
    country twin2 = t_country("Twin2", 200, 8);
    t_check(dense, sparse, -1);
    t_check(sparse, dense, 1);
    t_check(a, b, 1);
    t_check(b, a, -1);
    t_check(twin1, twin2, 0);
}
""", ["compare.c"])


# ---------------------------------------------------------------- swap

@check50.check(exists)
def swap_ints():
    """swap swaps two ints"""
    harness("swap_ints", r"""
int main(void)
{
    int a = 1, b = 2;
    swap(&a, &b, sizeof(int));
    EXPECT(a == 2 && b == 1, "after swap(&a, &b, sizeof(int)) with a = 1 and b = 2, a is %d and b is %d", a, b);
}
""", ["qsort.c"])


@check50.check(exists)
def swap_sizes():
    """swap swaps elements of 1, 7 and 24 bytes, and nothing around them"""
    harness("swap_sizes", r"""
typedef struct { char name[20]; int age; } t_person;
typedef struct { char bytes[7]; } t_odd;
int main(void)
{
    char c[3] = {'a', 'b', 'c'};
    swap(&c[0], &c[2], sizeof(char));
    EXPECT(c[0] == 'c' && c[1] == 'b' && c[2] == 'a', "swap with size 1 on {'a', 'b', 'c'} gave {'%c', '%c', '%c'}", c[0], c[1], c[2]);

    t_odd o[3] = {{"AAAAAA"}, {"BBBBBB"}, {"CCCCCC"}};
    swap(&o[0], &o[2], sizeof(t_odd));
    EXPECT(strcmp(o[0].bytes, "CCCCCC") == 0 && strcmp(o[1].bytes, "BBBBBB") == 0 && strcmp(o[2].bytes, "AAAAAA") == 0,
           "swap with size 7 did not swap the first and last of three 7-byte elements correctly");

    t_person p[2] = {{"Ada", 36}, {"Alan", 41}};
    swap(&p[0], &p[1], sizeof(t_person));
    EXPECT(strcmp(p[0].name, "Alan") == 0 && p[0].age == 41 && strcmp(p[1].name, "Ada") == 0 && p[1].age == 36,
           "swap with size sizeof(struct) did not swap two structs completely");
}
""", ["qsort.c"])


@check50.check(exists)
def swap_same_element():
    """swap with the same element twice leaves it unchanged"""
    harness("swap_same_element", r"""
int main(void)
{
    int a[3] = {7, 8, 9};
    swap(&a[1], &a[1], sizeof(int));
    EXPECT(a[0] == 7 && a[1] == 8 && a[2] == 9, "swap(&a[1], &a[1], sizeof(int)) changed the array into {%d, %d, %d}", a[0], a[1], a[2]);
}
""", ["qsort.c"])


# ---------------------------------------------------------------- qsort_

# Comparators and helpers of our own, so that qsort_ is tested on its own
OWN = r"""
static long t_compares = 0;
static const char *t_lo, *t_hi;

static void t_inside(const void *p)
{
    EXPECT((const char *) p >= t_lo && (const char *) p < t_hi,
           "qsort_ called compare with a pointer outside of the array");
}

static int t_int_asc(const void *a, const void *b)
{
    t_inside(a);
    t_inside(b);
    t_compares++;
    int x = *(const int *) a, y = *(const int *) b;
    return (x > y) - (x < y);
}

static int t_int_desc(const void *a, const void *b) { return t_int_asc(b, a); }

static int t_string(const void *a, const void *b)
{
    t_inside(a);
    t_inside(b);
    t_compares++;
    return strcmp(*(char * const *) a, *(char * const *) b);
}

static void t_range(const void *base, size_t n, size_t size)
{
    t_lo = base;
    t_hi = (const char *) base + n * size;
    t_compares = 0;
}

static int t_plain_int(const void *a, const void *b)
{
    int x = *(const int *) a, y = *(const int *) b;
    return (x > y) - (x < y);
}

// Sorts a copy with the standard qsort and compares: same elements, same order
static void t_check_ints(const char *what, int *a, const int *original, int n)
{
    int *want = malloc(n * sizeof(int));
    memcpy(want, original, n * sizeof(int));
    qsort(want, n, sizeof(int), t_plain_int);
    for (int i = 0; i < n; i++)
    {
        if (a[i] != want[i])
        {
            printf("%s: element %d should be %d but is %d\n", what, i, want[i], a[i]);
            exit(1);
        }
    }
    free(want);
}

static int t_next = 12345;
static int t_random(int below)
{
    t_next = (int) ((t_next * 1103515245L + 12345L) & 0x7fffffff);
    return (t_next >> 8) % below;
}
"""


def own_harness(name, main, **kwargs):
    harness(name, OWN + main, ["qsort.c"], **kwargs)


@check50.check(exists)
def qsort_small_ints():
    """qsort_ sorts {5, 2, 9, 1, 5, 6} into {1, 2, 5, 5, 6, 9}"""
    own_harness("small_ints", r"""
int main(void)
{
    int a[] = {5, 2, 9, 1, 5, 6};
    int want[] = {1, 2, 5, 5, 6, 9};
    t_range(a, 6, sizeof(int));
    qsort_(a, 6, sizeof(int), t_int_asc);
    t_expect_ints("qsort_(array, 6, sizeof(int), compare)", a, want, 6);
}
""")


@check50.check(exists)
def qsort_descending():
    """qsort_ follows the comparator: sorts from large to small"""
    own_harness("descending", r"""
int main(void)
{
    int a[] = {5, 2, 9, 1, 5, 6};
    int want[] = {9, 6, 5, 5, 2, 1};
    t_range(a, 6, sizeof(int));
    qsort_(a, 6, sizeof(int), t_int_desc);
    t_expect_ints("qsort_ with a comparator for descending order", a, want, 6);
}
""")


@check50.check(exists)
def qsort_tiny_arrays():
    """qsort_ handles arrays of 0, 1 and 2 elements"""
    own_harness("tiny", r"""
int main(void)
{
    int a[] = {3, 1, 2};
    int none[] = {3, 1, 2};
    t_range(a, 0, sizeof(int));
    qsort_(a, 0, sizeof(int), t_int_asc);
    t_expect_ints("qsort_(array, 0, ...) changed the array", a, none, 3);

    int one[] = {42, 7};
    int one_want[] = {42, 7};
    t_range(one, 1, sizeof(int));
    qsort_(one, 1, sizeof(int), t_int_asc);
    t_expect_ints("qsort_(array, 1, ...) changed the array", one, one_want, 2);

    int two[] = {9, 4, 1};
    int two_want[] = {4, 9, 1};
    t_range(two, 2, sizeof(int));
    qsort_(two, 2, sizeof(int), t_int_asc);
    t_expect_ints("qsort_(array, 2, ...) on {9, 4, 1}", two, two_want, 3);
}
""")


@check50.check(exists)
def qsort_respects_nmemb():
    """qsort_ only sorts the first nmemb elements"""
    own_harness("nmemb", r"""
int main(void)
{
    int a[] = {5, 4, 3, 2, 1, 0};
    int want[] = {3, 4, 5, 2, 1, 0};
    t_range(a, 3, sizeof(int));
    qsort_(a, 3, sizeof(int), t_int_asc);
    t_expect_ints("qsort_(array, 3, ...) on {5, 4, 3, 2, 1, 0}", a, want, 6);
}
""")


@check50.check(exists)
def qsort_random_ints():
    """qsort_ sorts 1000 random ints, with many duplicates, exactly like the standard qsort"""
    own_harness("random_ints", r"""
int main(void)
{
    int n = 1000;
    int *a = malloc(n * sizeof(int));
    int *original = malloc(n * sizeof(int));
    for (int i = 0; i < n; i++) { a[i] = original[i] = t_random(500) - 250; }
    t_range(a, n, sizeof(int));
    qsort_(a, n, sizeof(int), t_int_asc);
    t_check_ints("qsort_ on 1000 random ints", a, original, n);
}
""")


@check50.check(exists)
def qsort_strings():
    """qsort_ sorts an array of strings (char *)"""
    own_harness("strings", r"""
int main(void)
{
    char *w[] = {"pear", "apple", "fig", "banana", "cherry", "apple", "date"};
    char *want[] = {"apple", "apple", "banana", "cherry", "date", "fig", "pear"};
    t_range(w, 7, sizeof(char *));
    qsort_(w, 7, sizeof(char *), t_string);
    for (int i = 0; i < 7; i++)
    {
        EXPECT(strcmp(w[i], want[i]) == 0, "qsort_ on strings: element %d should be \"%s\" but is \"%s\"", i, want[i], w[i]);
    }
}
""")


@check50.check(exists)
def qsort_structs():
    """qsort_ sorts structs and moves each struct as a whole"""
    own_harness("structs", r"""
typedef struct { char name[20]; int age; } t_person;
static int t_by_age(const void *a, const void *b)
{
    t_inside(a);
    t_inside(b);
    t_compares++;
    return ((const t_person *) a)->age - ((const t_person *) b)->age;
}
int main(void)
{
    t_person p[] = {{"Ada", 36}, {"Tim", 9}, {"Alan", 41}, {"Eva", 14}, {"Grace", 85}, {"Linus", 28}};
    const char *names[] = {"Tim", "Eva", "Linus", "Ada", "Alan", "Grace"};
    int ages[] = {9, 14, 28, 36, 41, 85};
    t_range(p, 6, sizeof(t_person));
    qsort_(p, 6, sizeof(t_person), t_by_age);
    for (int i = 0; i < 6; i++)
    {
        EXPECT(strcmp(p[i].name, names[i]) == 0 && p[i].age == ages[i],
               "qsort_ on structs: element %d should be %s (%d) but is %s (%d)", i, names[i], ages[i], p[i].name, p[i].age);
    }
}
""")


@check50.check(exists)
def qsort_odd_element_size():
    """qsort_ works for elements of 3 bytes, so it really uses size"""
    own_harness("odd_size", r"""
typedef struct { unsigned char key; unsigned char tag[2]; } t_triple;
static int t_by_key(const void *a, const void *b)
{
    t_inside(a);
    t_inside(b);
    return (int) ((const t_triple *) a)->key - (int) ((const t_triple *) b)->key;
}
int main(void)
{
    t_triple t[] = {{5, "a"}, {3, "b"}, {9, "c"}, {1, "d"}, {7, "e"}};
    const char *tags = "dbaec";
    int keys[] = {1, 3, 5, 7, 9};
    t_range(t, 5, sizeof(t_triple));
    qsort_(t, 5, sizeof(t_triple), t_by_key);
    for (int i = 0; i < 5; i++)
    {
        EXPECT(t[i].key == keys[i] && t[i].tag[0] == (unsigned char) tags[i],
               "qsort_ on 3-byte elements: element %d should be key %d but has key %d", i, keys[i], t[i].key);
    }
}
""")


def _scaling(name, fill, description):
    """A qsort_ that is not O(n log n) on this input makes far too many comparisons"""
    own_harness(name, r"""
int main(void)
{
    int n = 50000;
    int *a = malloc(n * sizeof(int));
    int *original = malloc(n * sizeof(int));
    for (int i = 0; i < n; i++) { a[i] = %s; original[i] = a[i]; }
    t_range(a, n, sizeof(int));
    qsort_(a, n, sizeof(int), t_int_asc);
    EXPECT(t_compares <= (long) n * 16 * %d,
           "qsort_ on %s made %%ld comparisons, which is far too many for 50000 elements (it should be below %%ld)",
           t_compares, (long) n * 16 * %d);
    t_check_ints("qsort_ on %s", a, original, n);
}
""" % (fill, MAX_COMPARES_PER_N_LOG_N, description, MAX_COMPARES_PER_N_LOG_N, description), asan=False, timeout=15)


@check50.check(exists)
def qsort_sorted_input():
    """qsort_ stays fast on an already sorted array of 50000 ints"""
    _scaling("sorted", "i", "50000 sorted ints")


@check50.check(exists)
def qsort_reverse_input():
    """qsort_ stays fast on a reversed array of 50000 ints"""
    _scaling("reverse", "n - i", "50000 reversed ints")


@check50.check(exists)
def qsort_many_duplicates():
    """qsort_ stays fast on 50000 ints with only 1000 different values"""
    _scaling("duplicates", "t_random(1000)", "50000 ints with many duplicates")


@check50.check(exists)
def qsort_million():
    """qsort_ sorts a million random ints within a few seconds"""
    own_harness("million", r"""
int main(void)
{
    int n = 1000000;
    int *a = malloc(n * sizeof(int));
    int *original = malloc(n * sizeof(int));
    for (int i = 0; i < n; i++) { a[i] = original[i] = t_random(1000000); }
    t_range(a, n, sizeof(int));
    qsort_(a, n, sizeof(int), t_int_asc);
    t_check_ints("qsort_ on a million random ints", a, original, n);
}
""", asan=False, timeout=15)


# ---------------------------------------------------------------- the whole program

def sorter(arguments, timeout=10):
    """Run ./sorter and require its own verdict to be positive"""
    output = check50.run(f"./sorter {arguments}").stdout(timeout=timeout)
    lines = [line for line in output.splitlines() if line.strip()]

    if any("NOT sorted correctly" in line for line in lines):
        verdict = next(line for line in lines if "NOT sorted correctly" in line)
        raise check50.Failure(verdict.strip(),
                              help=f"Run ./sorter {arguments} yourself to look at the output.")

    if not lines or "Sorted correctly!" not in lines[-1]:
        raise check50.Failure("sorter did not report that the data is sorted correctly",
                              help=f"The last line of the output of ./sorter {arguments} was:\n"
                                   f"{lines[-1] if lines else '(nothing)'}")


@check50.check(compiles)
def sorter_numbers():
    """./sorter numbers sorts the numbers"""
    sorter("numbers")


@check50.check(compiles)
def sorter_numbers_desc():
    """./sorter numbers desc sorts the numbers from large to small"""
    sorter("numbers desc")


@check50.check(compiles)
def sorter_words():
    """./sorter words sorts the words alphabetically"""
    sorter("words")


@check50.check(compiles)
def sorter_words_length():
    """./sorter words length sorts the words by length"""
    sorter("words length")


@check50.check(compiles)
def sorter_countries_name():
    """./sorter countries name sorts the countries by name"""
    sorter("countries name")


@check50.check(compiles)
def sorter_countries_population():
    """./sorter countries population sorts the countries by population"""
    sorter("countries population")


@check50.check(compiles)
def sorter_countries_density():
    """./sorter countries density sorts the countries by density"""
    sorter("countries density")


@check50.check(compiles)
def sorter_bench():
    """./sorter bench 1000000 finishes within a few seconds, with the right result"""
    output = check50.run("./sorter bench 1000000").stdout(timeout=30)
    if "Results match." not in output:
        raise check50.Failure("qsort_ gave a different result than the standard qsort", help=output)
