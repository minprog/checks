import check50
import check50.c
import check50.internal

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)

@check50.check()
def exists():
    """functions.c exists"""
    check50.exists("functions.c")

@check50.check(exists)
def test_only_spaces_no_tabs():
    """functions.c only uses spaces for indentation (no tabs)"""
    with open("functions.c") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.startswith("\t"):
            line = line.rstrip("\n")
            raise check50.Failure(
                f"Tabs are used for indentation on line {i + 1}: {line}\n"
                f"    Check your editor's settings or the course's installation instructions on how to use spaces for indentation instead of tabs."
            )

@check50.check(test_only_spaces_no_tabs)
def compiles():
    """functions.c compiles"""
    check50.c.compile("functions.c", lcs50=True)

@check50.check(compiles)
def has_functions():
    """functions.c has the functions: times_two, print_int, half, print_float, average, and max"""
    with open("functions.c") as f:
        content = f.read()

    for name in ["times_two", "print_int", "half", "print_float", "average", "max"]:
        if f" {name}(" not in content:
            raise check50.Failure(f"Missing function: {name}")

@check50.check(has_functions)
def test_print_int():
    """print_int(3) prints Value = 3\\n"""
    main = (
        'int main(void) {\n'
        '    print_int(3);\n'
        '}'
    )

    with helpers.replace_main("functions.c", main):
        check50.c.compile("functions.c")
        check50.run("./functions").stdout("Value = 3").exit(0)

@check50.check(has_functions)
def test_times_two():
    """times_two(4) returns 8"""
    main = (
        'int main(void) {\n'
        '    printf("%d", times_two(4));\n'
        '}'
    )

    with helpers.replace_main("functions.c", main):
        check50.c.compile("functions.c")
        check50.run("./functions").stdout("8").exit(0)

@check50.check(has_functions)
def test_half():
    """half(6) returns 3"""
    main = (
        'int main(void) {\n'
        '    printf("%d", half(8));\n'
        '}'
    )

    with helpers.replace_main("functions.c", main):
        check50.c.compile("functions.c")
        check50.run("./functions").stdout("4").exit(0)

@check50.check(has_functions)
def test_print_float():
    """print_float(2.5) prints Value = 2.50\\n"""
    main = (
        'int main(void) {\n'
        '    print_float(2.5);\n'
        '}'
    )

    with helpers.replace_main("functions.c", main):
        check50.c.compile("functions.c")
        check50.run("./functions").stdout("Value = 2.50").exit(0)

@check50.check(test_print_float)
def test_average():
    """average(7, 4) returns 5.5"""
    main = (
        'int main(void) {\n'
        '    print_float(average(7, 4));\n'
        '}'
    )

    with helpers.replace_main("functions.c", main):
        check50.c.compile("functions.c")
        check50.run("./functions").stdout("Value = 5.50").exit(0)

@check50.check(test_print_float)
def test_max():
    """max(5.5, 9.0) returns 9.0"""
    main = (
        'int main(void) {\n'
        '    print_float(max(5.5, 9.0));\n'
        '}'
    )

    with helpers.replace_main("functions.c", main):
        check50.c.compile("functions.c")
        check50.run("./functions").stdout("Value = 9.00").exit(0)
