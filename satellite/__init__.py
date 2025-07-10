import check50
import check50.c
import check50.internal

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)

@check50.check()
def exists():
    "satellite.c exists"
    check50.exists("satellite.c")

@check50.check(exists)
def compiles():
    "satellite.c compiles"
    check50.c.compile("satellite.c", lcs50=True)

@check50.check(compiles)
def has_functions():
    "satellite.c has all required functions"
    with open("satellite.c") as f:
        content = f.read()

    for name in ["print_array", "fix_missing_values", "compute_running_average"]:
        if f" {name}(" not in content and f" {name} (" not in content:
            raise check50.Failure(f"Missing function: {name}")

@check50.check(has_functions)
def print_array():
    "print_array() prints the contents of the array separated by spaces"
    main = r"""
int main(void)
{
    int values1[] = {1, 3, 5, 3, 1};
    int n1 = 5;
    print_array(values1, n1);

    int values2[] = {1, 2, 28};
    int n2 = 3;
    print_array(values2, n2);

    int values3[] = {42};
    int n3 = 1;
    print_array(values3, n3);
}
"""
    with helpers.replace_main("satellite.c", main):
        check50.c.compile("satellite.c", lcs50=True)

        try:
            (check50.run("./satellite")
                .stdout("1, 3, 5, 3, 1")
                .stdout("1, 2, 28")
                .stdout("42")
            )
        except check50.Failure as f:
            f.payload["help"] = f"the following main function was used:\n{main}"
            raise f

@check50.check(print_array)
def test_fix_missing_values():
    "fix_missing_values() correctly replaces any missing values"
    main = r"""
int main(void)
{
    int values1[] = {1, -1, 3};
    fix_missing_values(values1, 3);
    print_array(values1, 3);

    int values2[] = {2, -1, 0, -1, 2};
    fix_missing_values(values2, 5);
    print_array(values2, 5);

    int values3[] = {2, 2, -1, 3};
    fix_missing_values(values3, 4);
    print_array(values3, 4);
}
"""
    with helpers.replace_main("satellite.c", main):
        check50.c.compile("satellite.c", lcs50=True)

        try:
            (check50.run("./satellite")
                .stdout("1, 2, 3\n", regex=False)
                .stdout("2, 1, 0, 1, 2\n", regex=False)
                .stdout("2, 2, 2, 3\n", regex=False)
            )
        except check50.Failure as f:
            f.payload["help"] = f"the following main function was used:\n{main}"
            raise f

@check50.check(print_array)
def test_compute_running_average():
    "compute_running_average() correctly applies a running average filter"
    main = r"""
int main(void)
{
    int values1[] = {1, 4, 3, 6, 3};
    compute_running_average(values1, 5);
    print_array(values1, 5);

    int values2[] = {1, 3, 5};
    compute_running_average(values2, 3);
    print_array(values2, 3);

    int values3[] = {1, 1};
    compute_running_average(values3, 2);
    print_array(values3, 2);
}
"""
    with helpers.replace_main("satellite.c", main):
        check50.c.compile("satellite.c", lcs50=True)
        
        try:
            (check50.run("./satellite")
                .stdout("1, 2, 4, 4, 3\n", regex=False)
                .stdout("1, 3, 5\n", regex=False)
                .stdout("1, 1\n", regex=False)
            )
        except check50.Failure as f:
            f.payload["help"] = f"the following main function was used:\n{main}"
            raise f
