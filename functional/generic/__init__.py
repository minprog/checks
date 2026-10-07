import check50
import check50.c
import check50.internal

common = check50.internal.import_file(
    "common",
    check50.internal.check_dir / "../_common.py"
)
FILE = "generic.c"

# Types the test programs use, to show that the functions work for any type
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
    """generic.c exists"""
    check50.exists(FILE)


@check50.check(exists)
def compiles():
    """generic.c compiles"""
    with common.helpers.replace_main(FILE, "int main(void) { return 0; }", show_main_in_help=False):
        check50.c.compile(FILE)


@check50.check(compiles)
def no_malloc():
    """does not use malloc"""
    common.no_malloc(FILE)


# ---------------------------------------------------------------- map

@check50.check(compiles)
def map_ints():
    """map adds 1 to every int in {1, 2, 3}"""
    run(r"""
static void t_inc(void *item) { *(int *) item += 1; }
int main(void)
{
    int a[] = {1, 2, 3};
    int want[] = {2, 3, 4};
    map(a, 3, sizeof(int), t_inc);
    t_expect_ints("map(array, 3, sizeof(int), inc)", a, want, 3);
}
""")


@check50.check(compiles)
def map_doubles():
    """map halves every double in {1.0, 5.0, 3.0}"""
    run(r"""
static void t_halve(void *item) { double *x = item; *x = *x / 2; }
int main(void)
{
    double a[] = {1.0, 5.0, 3.0};
    map(a, 3, sizeof(double), t_halve);
    EXPECT(a[0] == 0.5 && a[1] == 2.5 && a[2] == 1.5,
           "map(array, 3, sizeof(double), halve): expected {0.5, 2.5, 1.5} but found {%g, %g, %g}",
           a[0], a[1], a[2]);
}
""")


@check50.check(compiles)
def map_chars():
    """map works on elements of 1 byte: uppercases "hello" """
    run(r"""
static void t_upper(void *item) { char *c = item; if (*c >= 'a' && *c <= 'z') { *c = *c - 'a' + 'A'; } }
int main(void)
{
    char s[] = "hello";
    map(s, 5, sizeof(char), t_upper);
    EXPECT(strcmp(s, "HELLO") == 0, "map(\"hello\", 5, sizeof(char), upper): expected \"HELLO\" but found \"%s\"", s);
}
""")


@check50.check(compiles)
def map_structs():
    """map works on structs: makes everyone one year older"""
    run(r"""
static void t_birthday(void *item) { ((t_person *) item)->age += 1; }
int main(void)
{
    t_person people[] = {{"Ada", 36}, {"Alan", 41}, {"Grace", 85}};
    int want[] = {37, 42, 86};
    const char *names[] = {"Ada", "Alan", "Grace"};
    map(people, 3, sizeof(t_person), t_birthday);
    for (int i = 0; i < 3; i++)
    {
        EXPECT(people[i].age == want[i], "person %d: expected age %d but found %d", i, want[i], people[i].age);
        EXPECT(strcmp(people[i].name, names[i]) == 0, "person %d: expected name \"%s\" but found \"%s\"", i, names[i], people[i].name);
    }
}
""")


@check50.check(compiles)
def map_gives_pointer_to_each_element():
    """map calls f once per element, with a pointer to that element, in order"""
    run(r"""
static char *t_base;
static size_t t_size;
static int t_calls = 0;
static void t_check(void *item)
{
    EXPECT(item == t_base + t_calls * t_size,
           "call %d of f got a pointer to byte %ld of the array, expected byte %zu",
           t_calls, (long) ((char *) item - t_base), t_calls * t_size);
    t_calls++;
}
int main(void)
{
    t_person people[4] = {{"A", 1}, {"B", 2}, {"C", 3}, {"D", 4}};
    t_base = (char *) people;
    t_size = sizeof(t_person);
    map(people, 4, sizeof(t_person), t_check);
    EXPECT(t_calls == 4, "map(array, 4, ...) called f %d times, expected 4", t_calls);
}
""")


@check50.check(compiles)
def map_empty():
    """map with n == 0 never calls f"""
    run(r"""
static int t_calls = 0;
static void t_count(void *item) { (void) item; t_calls++; }
int main(void)
{
    int a[] = {1, 2, 3};
    map(a, 0, sizeof(int), t_count);
    EXPECT(t_calls == 0, "map(array, 0, ...) called f %d time(s), expected 0 calls", t_calls);
}
""")


@check50.check(compiles)
def map_respects_n():
    """map leaves elements after the first n alone"""
    run(r"""
static void t_zero(void *item) { *(int *) item = 0; }
int main(void)
{
    int a[] = {1, 2, 3, 4, 5};
    int want[] = {0, 0, 3, 4, 5};
    map(a, 2, sizeof(int), t_zero);
    t_expect_ints("map(array, 2, ...) on an array of 5", a, want, 5);
}
""")


# ---------------------------------------------------------------- filter

@check50.check(compiles)
def filter_ints():
    """filter keeps the even ints of {5, 2, 8, 3, 6, 1}"""
    run(r"""
static bool t_even(const void *item) { return *(const int *) item % 2 == 0; }
int main(void)
{
    int a[] = {5, 2, 8, 3, 6, 1};
    int want[] = {2, 8, 6};
    size_t m = filter(a, 6, sizeof(int), t_even);
    EXPECT(m == 3, "filter(array, 6, sizeof(int), is_even) returned %zu, expected 3", m);
    t_expect_ints("filter(array, 6, sizeof(int), is_even), first 3 elements", a, want, 3);
}
""")


@check50.check(compiles)
def filter_strings():
    """filter keeps the strings longer than 4 characters"""
    run(r"""
static bool t_long(const void *item) { return strlen(*(char * const *) item) > 4; }
int main(void)
{
    char *words[] = {"appel", "peer", "aardbei", "kers", "banaan"};
    char *want[] = {"appel", "aardbei", "banaan"};
    size_t m = filter(words, 5, sizeof(char *), t_long);
    EXPECT(m == 3, "filter(words, 5, sizeof(char *), is_long) returned %zu, expected 3", m);
    for (int i = 0; i < 3; i++)
    {
        EXPECT(words[i] != NULL && strcmp(words[i], want[i]) == 0,
               "filter on words: word %d should be \"%s\" but is \"%s\"", i, want[i], words[i] ? words[i] : "(null)");
    }
}
""")


@check50.check(compiles)
def filter_chars():
    """filter works on elements of 1 byte: keeps only the letters of "a1b2c3" """
    run(r"""
static bool t_letter(const void *item) { char c = *(const char *) item; return c >= 'a' && c <= 'z'; }
int main(void)
{
    char s[] = "a1b2c3";
    size_t m = filter(s, 6, sizeof(char), t_letter);
    EXPECT(m == 3, "filter(\"a1b2c3\", 6, sizeof(char), is_letter) returned %zu, expected 3", m);
    EXPECT(strncmp(s, "abc", 3) == 0, "filter(\"a1b2c3\", ...): expected the first 3 characters to be \"abc\" but found \"%.3s\"", s);
}
""")


@check50.check(compiles)
def filter_structs():
    """filter keeps adults in an array of structs, copying each struct completely"""
    run(r"""
static bool t_adult(const void *item) { return ((const t_person *) item)->age >= 18; }
int main(void)
{
    t_person people[] = {{"Ada", 36}, {"Tim", 9}, {"Alan", 41}, {"Eva", 17}, {"Grace", 85}};
    const char *names[] = {"Ada", "Alan", "Grace"};
    int ages[] = {36, 41, 85};
    size_t m = filter(people, 5, sizeof(t_person), t_adult);
    EXPECT(m == 3, "filter(people, 5, sizeof(t_person), is_adult) returned %zu, expected 3", m);
    for (int i = 0; i < 3; i++)
    {
        EXPECT(strcmp(people[i].name, names[i]) == 0 && people[i].age == ages[i],
               "person %d: expected %s (%d) but found %s (%d)", i, names[i], ages[i], people[i].name, people[i].age);
    }
}
""")


@check50.check(compiles)
def filter_keeps_all():
    """filter returns n and changes nothing when every element is kept"""
    run(r"""
static bool t_yes(const void *item) { (void) item; return true; }
int main(void)
{
    int a[] = {4, 3, 2, 1};
    int want[] = {4, 3, 2, 1};
    size_t m = filter(a, 4, sizeof(int), t_yes);
    EXPECT(m == 4, "filter with a predicate that is always true returned %zu, expected 4", m);
    t_expect_ints("filter with a predicate that is always true", a, want, 4);
}
""")


@check50.check(compiles)
def filter_removes_all():
    """filter returns 0 when no element is kept"""
    run(r"""
static bool t_no(const void *item) { (void) item; return false; }
int main(void)
{
    int a[] = {4, 3, 2, 1};
    size_t m = filter(a, 4, sizeof(int), t_no);
    EXPECT(m == 0, "filter with a predicate that is always false returned %zu, expected 0", m);
}
""")


@check50.check(compiles)
def filter_empty():
    """filter with n == 0 returns 0 and never calls the predicate"""
    run(r"""
static int t_calls = 0;
static bool t_count(const void *item) { (void) item; t_calls++; return true; }
int main(void)
{
    int a[] = {1, 2, 3};
    size_t m = filter(a, 0, sizeof(int), t_count);
    EXPECT(m == 0, "filter(array, 0, ...) returned %zu, expected 0", m);
    EXPECT(t_calls == 0, "filter(array, 0, ...) called keep %d time(s), expected 0 calls", t_calls);
}
""")


@check50.check(compiles)
def filter_respects_n():
    """filter does not look at or change elements after the first n"""
    run(r"""
static bool t_even(const void *item) { return *(const int *) item % 2 == 0; }
int main(void)
{
    int a[] = {1, 2, 3, 4, 6, 8};
    int want[] = {2, 4};
    size_t m = filter(a, 4, sizeof(int), t_even);
    EXPECT(m == 2, "filter(array, 4, ...) on {1, 2, 3, 4, 6, 8} returned %zu, expected 2", m);
    t_expect_ints("filter(array, 4, ...), first 2 elements", a, want, 2);
    EXPECT(a[4] == 6 && a[5] == 8, "filter(array, 4, ...) changed elements after the first 4");
}
""")


@check50.check(compiles)
def filter_calls_keep_once_per_element():
    """filter calls keep exactly once for every element, from left to right"""
    run(r"""
static int t_seen[16];
static int t_calls = 0;
static bool t_record(const void *item)
{
    int x = *(const int *) item;
    if (t_calls < 16) { t_seen[t_calls] = x; }
    t_calls++;
    return x > 25;
}
int main(void)
{
    int a[] = {10, 20, 30, 40, 50};
    int original[] = {10, 20, 30, 40, 50};
    filter(a, 5, sizeof(int), t_record);
    EXPECT(t_calls == 5, "filter(array, 5, ...) called keep %d times, expected 5", t_calls);
    t_expect_ints("filter should call keep with the elements in order", t_seen, original, 5);
}
""")


@check50.check(compiles)
def map_then_filter():
    """map and filter can be combined"""
    run(r"""
static void t_square(void *item) { double *x = item; *x = *x * *x; }
static bool t_big(const void *item) { return *(const double *) item > 10; }
int main(void)
{
    double a[] = {1, 2, 3, 4, 5, 6};
    map(a, 6, sizeof(double), t_square);
    size_t m = filter(a, 6, sizeof(double), t_big);
    EXPECT(m == 3, "after squaring and filtering, filter returned %zu, expected 3", m);
    EXPECT(a[0] == 16 && a[1] == 25 && a[2] == 36,
           "expected {16, 25, 36} but found {%g, %g, %g}", a[0], a[1], a[2]);
}
""")
