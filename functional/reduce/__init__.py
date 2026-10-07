import re

import check50
import check50.c
import check50.internal

common = check50.internal.import_file(
    "common",
    check50.internal.check_dir / "../_common.py"
)
FILE = "reduce.c"

TYPES = r"""
typedef struct
{
    char name[20];
    int age;
}
t_person;
"""


def run(main, **kwargs):
    common.run_test(FILE, TYPES + main, **kwargs)


@check50.check()
def exists():
    """reduce.c exists"""
    check50.exists(FILE)


@check50.check(exists)
def compiles():
    """reduce.c compiles"""
    with common.helpers.replace_main(FILE, "int main(void) { return 0; }", show_main_in_help=False):
        check50.c.compile(FILE)


@check50.check(compiles)
def sum_ints():
    """reduce sums the ints {3, 1, 4, 1, 5} into 14"""
    run(r"""
static void t_add(void *acc, const void *item) { *(int *) acc += *(const int *) item; }
int main(void)
{
    int a[] = {3, 1, 4, 1, 5};
    int sum = 0;
    reduce(a, 5, sizeof(int), &sum, t_add);
    EXPECT(sum == 14, "reduce(array, 5, sizeof(int), &sum, add) left sum at %d, expected 14", sum);
}
""")


@check50.check(compiles)
def product_doubles():
    """reduce multiplies the doubles {1.5, 2, 4} into 12"""
    run(r"""
static void t_mul(void *acc, const void *item) { *(double *) acc *= *(const double *) item; }
int main(void)
{
    double a[] = {1.5, 2.0, 4.0};
    double product = 1.0;
    reduce(a, 3, sizeof(double), &product, t_mul);
    EXPECT(product == 12.0, "reduce(array, 3, sizeof(double), &product, mul) left product at %g, expected 12", product);
}
""")


@check50.check(compiles)
def longest_string():
    """reduce finds the longest string in {"appel", "peer", "aardbei", "kers"}"""
    run(r"""
static void t_longest(void *acc, const void *item)
{
    const char *current = *(char **) acc;
    const char *candidate = *(char * const *) item;
    if (strlen(candidate) > strlen(current))
    {
        *(const char **) acc = candidate;
    }
}
int main(void)
{
    char *words[] = {"appel", "peer", "aardbei", "kers"};
    char *best = "";
    reduce(words, 4, sizeof(char *), &best, t_longest);
    EXPECT(strcmp(best, "aardbei") == 0, "reduce for the longest word found \"%s\", expected \"aardbei\"", best);
}
""")


@check50.check(compiles)
def struct_average():
    """reduce computes the average age of an array of structs"""
    run(r"""
typedef struct { int sum; int count; } t_total;
static void t_tally(void *acc, const void *item)
{
    t_total *total = acc;
    total->sum += ((const t_person *) item)->age;
    total->count += 1;
}
int main(void)
{
    t_person people[] = {{"Ada", 36}, {"Tim", 9}, {"Alan", 41}, {"Eva", 14}};
    t_total total = {0, 0};
    reduce(people, 4, sizeof(t_person), &total, t_tally);
    EXPECT(total.count == 4, "reduce visited %d of the 4 persons", total.count);
    EXPECT(total.sum == 100, "the ages add up to %d, expected 100", total.sum);
}
""")


@check50.check(compiles)
def visits_in_order():
    """reduce visits the elements from front to back: collects "abcde" in order"""
    run(r"""
static void t_append(void *acc, const void *item)
{
    char *s = acc;
    size_t len = strlen(s);
    s[len] = *(const char *) item;
    s[len + 1] = '\0';
}
int main(void)
{
    char letters[] = {'a', 'b', 'c', 'd', 'e'};
    char collected[16] = "";
    reduce(letters, 5, sizeof(char), collected, t_append);
    EXPECT(strcmp(collected, "abcde") == 0, "reduce collected \"%s\", expected \"abcde\"", collected);
}
""")


@check50.check(compiles)
def gives_pointer_to_each_element():
    """reduce calls f once per element, with the accumulator and a pointer to that element"""
    run(r"""
static char *t_base;
static size_t t_size;
static void *t_acc;
static int t_calls = 0;
static void t_check(void *acc, const void *item)
{
    EXPECT(acc == t_acc, "call %d of f got a different accumulator than the one passed to reduce", t_calls);
    EXPECT((const char *) item == t_base + t_calls * t_size,
           "call %d of f got a pointer to byte %ld of the array, expected byte %zu",
           t_calls, (long) ((const char *) item - t_base), t_calls * t_size);
    t_calls++;
}
int main(void)
{
    t_person people[4] = {{"A", 1}, {"B", 2}, {"C", 3}, {"D", 4}};
    int acc = 0;
    t_base = (char *) people;
    t_size = sizeof(t_person);
    t_acc = &acc;
    reduce(people, 4, sizeof(t_person), &acc, t_check);
    EXPECT(t_calls == 4, "reduce(array, 4, ...) called f %d times, expected 4", t_calls);
}
""")


@check50.check(compiles)
def single_element():
    """reduce works on an array with one element"""
    run(r"""
static void t_add(void *acc, const void *item) { *(int *) acc += *(const int *) item; }
int main(void)
{
    int a[] = {42};
    int sum = 8;
    reduce(a, 1, sizeof(int), &sum, t_add);
    EXPECT(sum == 50, "reduce on one element {42} with sum starting at 8 left sum at %d, expected 50", sum);
}
""")


@check50.check(compiles)
def empty():
    """reduce with n == 0 never calls f and leaves the accumulator alone"""
    run(r"""
static int t_calls = 0;
static void t_count(void *acc, const void *item) { (void) acc; (void) item; t_calls++; }
int main(void)
{
    int a[] = {1, 2, 3};
    int acc = 7;
    reduce(a, 0, sizeof(int), &acc, t_count);
    EXPECT(t_calls == 0, "reduce(array, 0, ...) called f %d time(s), expected 0 calls", t_calls);
    EXPECT(acc == 7, "reduce(array, 0, ...) changed the accumulator to %d", acc);
}
""")


@check50.check(compiles)
def respects_n():
    """reduce only visits the first n elements"""
    run(r"""
static void t_add(void *acc, const void *item) { *(int *) acc += *(const int *) item; }
int main(void)
{
    int a[] = {1, 2, 3, 4, 5};
    int sum = 0;
    reduce(a, 3, sizeof(int), &sum, t_add);
    EXPECT(sum == 6, "reduce(array, 3, ...) on {1, 2, 3, 4, 5} left sum at %d, expected 6", sum);
}
""")


@check50.check(compiles)
def does_not_change_items():
    """reduce does not change the array itself"""
    run(r"""
static void t_add(void *acc, const void *item) { *(int *) acc += *(const int *) item; }
int main(void)
{
    int a[] = {3, 1, 4, 1, 5};
    int want[] = {3, 1, 4, 1, 5};
    int sum = 0;
    reduce(a, 5, sizeof(int), &sum, t_add);
    t_expect_ints("reduce changed the array", a, want, 5);
}
""")


# ---------------------------------------------------------------- using reduce

# The assignment leaves the accumulator (a number, a struct, ...) and the
# functions handed to reduce to the student, so these checks can only look at
# what the three functions do and at how they are written: their bodies have to
# call reduce, and may not contain a loop of their own.


def _body(name):
    return common.function_body(common.read_source(FILE), name, FILE)


def _uses_reduce_without_loop(name):
    body = _body(name)
    if not re.search(r"\breduce\s*\(", body):
        raise check50.Failure(f"{name} does not call reduce",
                              help=f"{name} has to use reduce to do its work.")
    loop = re.search(r"\b(for|while|do|goto)\b", body)
    if loop:
        raise check50.Failure(f"{name} contains a loop of its own ({loop.group(1)})",
                              help=f"Looping over the array is the job of reduce, so {name} should not loop itself.")


def run_function(name, main):
    _body(name)
    run("#include <math.h>\n#define T_CLOSE(a, b) (fabs((a) - (b)) < 1e-9)\n" + main)


@check50.check(compiles)
def max_double_uses_reduce():
    """max_double calls reduce and has no loop of its own"""
    _uses_reduce_without_loop("max_double")


@check50.check(compiles)
def max_double_works():
    """max_double finds the largest of {2.5, 9.0, 4.0}, and of arrays with only negative numbers"""
    run_function("max_double", r"""
int main(void)
{
    double a[] = {2.5, 9.0, 4.0};
    double got = max_double(a, 3);
    EXPECT(T_CLOSE(got, 9.0), "max_double({2.5, 9.0, 4.0}, 3) returned %g, expected 9", got);

    double first[] = {9.0, 1.0, 2.0};
    got = max_double(first, 3);
    EXPECT(T_CLOSE(got, 9.0), "max_double({9.0, 1.0, 2.0}, 3) returned %g, expected 9", got);

    double last[] = {1.0, 2.0, 9.0};
    got = max_double(last, 3);
    EXPECT(T_CLOSE(got, 9.0), "max_double({1.0, 2.0, 9.0}, 3) returned %g, expected 9", got);

    double negative[] = {-5.5, -2.25, -9.0};
    got = max_double(negative, 3);
    EXPECT(T_CLOSE(got, -2.25), "max_double({-5.5, -2.25, -9.0}, 3) returned %g, expected -2.25", got);

    double one[] = {-1.0};
    got = max_double(one, 1);
    EXPECT(T_CLOSE(got, -1.0), "max_double({-1.0}, 1) returned %g, expected -1", got);
}
""")


@check50.check(compiles)
def count_a_uses_reduce():
    """count_a calls reduce and has no loop of its own"""
    _uses_reduce_without_loop("count_a")


@check50.check(compiles)
def count_a_works():
    """count_a counts the strings that start with a lowercase a"""
    run_function("count_a", r"""
int main(void)
{
    char *words[] = {"appel", "peer", "aardbei", "Aap"};
    int got = count_a(words, 4);
    EXPECT(got == 2, "count_a({\"appel\", \"peer\", \"aardbei\", \"Aap\"}, 4) returned %d, expected 2", got);

    char *none[] = {"peer", "kers", "banaan", "bal"};
    got = count_a(none, 4);
    EXPECT(got == 0, "count_a({\"peer\", \"kers\", \"banaan\", \"bal\"}, 4) returned %d, expected 0", got);

    char *tricky[] = {"", "a", "ba", "ab", "A"};
    got = count_a(tricky, 5);
    EXPECT(got == 2, "count_a({\"\", \"a\", \"ba\", \"ab\", \"A\"}, 5) returned %d, expected 2", got);

    got = count_a(words, 0);
    EXPECT(got == 0, "count_a(words, 0) returned %d, expected 0", got);

    got = count_a(words, 1);
    EXPECT(got == 1, "count_a(words, 1) on {\"appel\", ...} returned %d, expected 1", got);
}
""")


@check50.check(compiles)
def average_uses_reduce():
    """average calls reduce and has no loop of its own"""
    _uses_reduce_without_loop("average")


@check50.check(compiles)
def average_works():
    """average computes {4, 8, 15, 16, 23, 42} into 18.0 and {1, 2} into 1.5"""
    run_function("average", r"""
int main(void)
{
    int ages[] = {4, 8, 15, 16, 23, 42};
    double got = average(ages, 6);
    EXPECT(T_CLOSE(got, 18.0), "average({4, 8, 15, 16, 23, 42}, 6) returned %g, expected 18", got);

    int two[] = {1, 2};
    got = average(two, 2);
    EXPECT(T_CLOSE(got, 1.5), "average({1, 2}, 2) returned %g, expected 1.5", got);

    int mixed[] = {-3, 3, -7, 7};
    got = average(mixed, 4);
    EXPECT(T_CLOSE(got, 0.0), "average({-3, 3, -7, 7}, 4) returned %g, expected 0", got);

    int one[] = {7};
    got = average(one, 1);
    EXPECT(T_CLOSE(got, 7.0), "average({7}, 1) returned %g, expected 7", got);
}
""")


@check50.check(compiles)
def average_empty():
    """average of an empty array is 0.0"""
    run_function("average", r"""
int main(void)
{
    int a[] = {1, 2, 3};
    double got = average(a, 0);
    EXPECT(T_CLOSE(got, 0.0), "average(array, 0) returned %g, expected 0", got);
}
""")


@check50.check(compiles)
def average_big_numbers():
    """average is correct when the sum no longer fits in an int"""
    run_function("average", r"""
int main(void)
{
    int a[] = {2000000000, 2000000000, 2000000000};
    double got = average(a, 3);
    EXPECT(T_CLOSE(got, 2000000000.0),
           "average({2000000000, 2000000000, 2000000000}, 3) returned %.1f, expected 2000000000.0", got);
}
""")
