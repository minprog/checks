import check50
import check50.c
import check50.internal

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)

@check50.check()
def exists():
    """binary.c exists"""
    check50.exists("binary.c")

@check50.check(exists)
def compiles():
    """binary.c compiles"""
    check50.c.compile("binary.c", lcs50=True)

@check50.check(compiles)
def has_functions():
    """binary.c has the function to_decimal"""
    with open("binary.c") as f:
        content = f.read()

    for name in ["to_decimal"]:
        if f" {name}(" not in content:
            raise check50.Failure(f"Missing function: {name}")

@check50.check(has_functions)
def test_to_decimal_0():
    """to_decimal(0, 0, 0, 0) returns 0"""
    main = (
        'int main(void) {\n'
        '    printf("%d", to_decimal(0, 0, 0, 0));\n'
        '}'
    )

    with helpers.replace_main("binary.c", main):
        check50.c.compile("binary.c")
        check50.run("./binary").stdout("0").exit(0)

@check50.check(has_functions)
def test_to_decimal_1():
    """to_decimal(0, 0, 0, 1) returns 1"""
    main = (
        'int main(void) {\n'
        '    printf("%d", to_decimal(0, 0, 0, 1));\n'
        '}'
    )

    with helpers.replace_main("binary.c", main):
        check50.c.compile("binary.c")
        check50.run("./binary").stdout("1").exit(0)

@check50.check(has_functions)
def test_to_decimal_5():
    """to_decimal(0, 1, 0, 1) returns 5"""
    main = (
        'int main(void) {\n'
        '    printf("%d", to_decimal(0, 1, 0, 1));\n'
        '}'
    )

    with helpers.replace_main("binary.c", main):
        check50.c.compile("binary.c")
        check50.run("./binary").stdout("5").exit(0)

@check50.check(has_functions)
def test_to_decimal_15():
    """to_decimal(1, 1, 1, 1) returns 15"""
    main = (
        'int main(void) {\n'
        '    printf("%d", to_decimal(1, 1, 1, 1));\n'
        '}'
    )

    with helpers.replace_main("binary.c", main):
        check50.c.compile("binary.c")
        check50.run("./binary").stdout("15").exit(0)