import check50
import check50.c
import check50.internal

common = check50.internal.import_file(
    "common",
    check50.internal.check_dir / "../_common.py"
)
FILE = "map_filter.c"


def run(main, **kwargs):
    common.run_test(FILE, main, **kwargs)


@check50.check()
def exists():
    """map_filter.c exists"""
    check50.exists(FILE)


@check50.check(exists)
def compiles():
    """map_filter.c compiles"""
    with common.helpers.replace_main(FILE, "int main(void) { return 0; }", show_main_in_help=False):
        check50.c.compile(FILE)


@check50.check(compiles)
def no_malloc():
    """does not use malloc"""
    common.no_malloc(FILE)


# ---------------------------------------------------------------- map_int

@check50.check(compiles)
def map_square():
    """map_int squares {1, 2, 3, 4} into {1, 4, 9, 16}"""
    run(r"""
static int t_square(int x) { return x * x; }
int main(void)
{
    int a[] = {1, 2, 3, 4};
    int want[] = {1, 4, 9, 16};
    map_int(a, 4, t_square);
    t_expect_ints("map_int(array, 4, square)", a, want, 4);
}
""")


@check50.check(compiles)
def map_abs():
    """map_int with abs turns {-3, 0, 5, -7} into {3, 0, 5, 7}"""
    run(r"""
static int t_abs(int x) { return x < 0 ? -x : x; }
int main(void)
{
    int a[] = {-3, 0, 5, -7};
    int want[] = {3, 0, 5, 7};
    map_int(a, 4, t_abs);
    t_expect_ints("map_int(array, 4, abs)", a, want, 4);
}
""")


@check50.check(compiles)
def map_ignores_value():
    """map_int works with a function that ignores its argument"""
    run(r"""
static int t_seven(int x) { (void) x; return 7; }
int main(void)
{
    int a[] = {1, 2, 3};
    int want[] = {7, 7, 7};
    map_int(a, 3, t_seven);
    t_expect_ints("map_int(array, 3, seven)", a, want, 3);
}
""")


@check50.check(compiles)
def map_single():
    """map_int works on an array with one element"""
    run(r"""
static int t_negate(int x) { return -x; }
int main(void)
{
    int a[] = {42};
    int want[] = {-42};
    map_int(a, 1, t_negate);
    t_expect_ints("map_int(array, 1, negate)", a, want, 1);
}
""")


@check50.check(compiles)
def map_empty():
    """map_int with n == 0 does nothing and never calls f"""
    run(r"""
static int t_calls = 0;
static int t_count(int x) { t_calls++; return x + 1; }
int main(void)
{
    int a[] = {1, 2, 3};
    int want[] = {1, 2, 3};
    map_int(a, 0, t_count);
    EXPECT(t_calls == 0, "map_int(array, 0, f) called f %d time(s), expected 0 calls", t_calls);
    t_expect_ints("map_int(array, 0, f) changed the array", a, want, 3);
}
""")


@check50.check(compiles)
def map_respects_n():
    """map_int only changes the first n elements"""
    run(r"""
static int t_double(int x) { return 2 * x; }
int main(void)
{
    int a[] = {1, 2, 3, 4, 5};
    int want[] = {2, 4, 6, 4, 5};
    map_int(a, 3, t_double);
    t_expect_ints("map_int(array, 3, double) on an array of 5", a, want, 5);
}
""")


@check50.check(compiles)
def map_calls_f_once_per_element():
    """map_int calls f exactly once for every element, from left to right"""
    run(r"""
static int t_seen[16];
static int t_calls = 0;
static int t_record(int x)
{
    if (t_calls < 16) { t_seen[t_calls] = x; }
    t_calls++;
    return x;
}
int main(void)
{
    int a[] = {10, 20, 30, 40, 50};
    map_int(a, 5, t_record);
    EXPECT(t_calls == 5, "map_int(array, 5, f) called f %d times, expected 5", t_calls);
    t_expect_ints("map_int should call f with the elements in order", t_seen, a, 5);
}
""")


# ---------------------------------------------------------------- filter_int

@check50.check(compiles)
def filter_even():
    """filter_int keeps the even numbers of {5, 2, 8, 3, 6, 1}"""
    run(r"""
static bool t_even(int x) { return x % 2 == 0; }
int main(void)
{
    int a[] = {5, 2, 8, 3, 6, 1};
    int want[] = {2, 8, 6};
    int m = filter_int(a, 6, t_even);
    EXPECT(m == 3, "filter_int(array, 6, is_even) returned %d, expected 3", m);
    t_expect_ints("filter_int(array, 6, is_even), first 3 elements", a, want, 3);
}
""")


@check50.check(compiles)
def filter_keeps_order():
    """filter_int keeps the original order of the elements it keeps"""
    run(r"""
static bool t_positive(int x) { return x > 0; }
int main(void)
{
    int a[] = {3, -1, 4, -1, 5, -9, 2, 6};
    int want[] = {3, 4, 5, 2, 6};
    int m = filter_int(a, 8, t_positive);
    EXPECT(m == 5, "filter_int(array, 8, is_positive) returned %d, expected 5", m);
    t_expect_ints("filter_int(array, 8, is_positive), first 5 elements", a, want, 5);
}
""")


@check50.check(compiles)
def filter_keeps_all():
    """filter_int returns n and changes nothing when every element is kept"""
    run(r"""
static bool t_yes(int x) { (void) x; return true; }
int main(void)
{
    int a[] = {4, 3, 2, 1};
    int want[] = {4, 3, 2, 1};
    int m = filter_int(a, 4, t_yes);
    EXPECT(m == 4, "filter_int with a predicate that is always true returned %d, expected 4", m);
    t_expect_ints("filter_int with a predicate that is always true", a, want, 4);
}
""")


@check50.check(compiles)
def filter_removes_all():
    """filter_int returns 0 when no element is kept"""
    run(r"""
static bool t_no(int x) { (void) x; return false; }
int main(void)
{
    int a[] = {4, 3, 2, 1};
    int m = filter_int(a, 4, t_no);
    EXPECT(m == 0, "filter_int with a predicate that is always false returned %d, expected 0", m);
}
""")


@check50.check(compiles)
def filter_empty():
    """filter_int with n == 0 returns 0 and never calls the predicate"""
    run(r"""
static int t_calls = 0;
static bool t_count(int x) { (void) x; t_calls++; return true; }
int main(void)
{
    int a[] = {1, 2, 3};
    int want[] = {1, 2, 3};
    int m = filter_int(a, 0, t_count);
    EXPECT(m == 0, "filter_int(array, 0, keep) returned %d, expected 0", m);
    EXPECT(t_calls == 0, "filter_int(array, 0, keep) called keep %d time(s), expected 0 calls", t_calls);
    t_expect_ints("filter_int(array, 0, keep) changed the array", a, want, 3);
}
""")


@check50.check(compiles)
def filter_respects_n():
    """filter_int does not look at or change elements after the first n"""
    run(r"""
static bool t_even(int x) { return x % 2 == 0; }
int main(void)
{
    int a[] = {1, 2, 3, 4, 6, 8};
    int m = filter_int(a, 4, t_even);
    int want[] = {2, 4};
    EXPECT(m == 2, "filter_int(array, 4, is_even) on {1, 2, 3, 4, 6, 8} returned %d, expected 2", m);
    t_expect_ints("filter_int(array, 4, is_even), first 2 elements", a, want, 2);
    EXPECT(a[4] == 6 && a[5] == 8, "filter_int(array, 4, f) changed elements after the first 4");
}
""")


@check50.check(compiles)
def filter_calls_keep_once_per_element():
    """filter_int calls keep exactly once for every element, from left to right"""
    run(r"""
static int t_seen[16];
static int t_calls = 0;
static bool t_record(int x)
{
    if (t_calls < 16) { t_seen[t_calls] = x; }
    t_calls++;
    return x > 25;
}
int main(void)
{
    int a[] = {10, 20, 30, 40, 50};
    int original[] = {10, 20, 30, 40, 50};
    filter_int(a, 5, t_record);
    EXPECT(t_calls == 5, "filter_int(array, 5, keep) called keep %d times, expected 5", t_calls);
    t_expect_ints("filter_int should call keep with the elements in order", t_seen, original, 5);
}
""")


@check50.check(compiles)
def map_then_filter():
    """map_int and filter_int can be combined: square 1..6, keep those above 10"""
    run(r"""
static int t_square(int x) { return x * x; }
static bool t_big(int x) { return x > 10; }
int main(void)
{
    int a[] = {1, 2, 3, 4, 5, 6};
    int want[] = {16, 25, 36};
    map_int(a, 6, t_square);
    int m = filter_int(a, 6, t_big);
    EXPECT(m == 3, "after squaring and filtering, filter_int returned %d, expected 3", m);
    t_expect_ints("squared numbers above 10", a, want, 3);
}
""")
