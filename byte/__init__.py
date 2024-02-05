import check50
import check50.c
import check50.internal

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)

@check50.check()
def exists():
    """byte.c exists"""
    check50.exists("byte.c")

@check50.check(exists)
def compiles():
    """byte.c compiles"""
    check50.c.compile("byte.c", lcs50=True)

@check50.check(compiles)
def has_functions():
    """byte.c has the function print_byte"""
    with open("byte.c") as f:
        content = f.read()

    for name in ["print_byte"]:
        if f" {name}(" not in content:
            raise check50.Failure(f"Missing function: {name}")

@check50.check(has_functions)
def test_print_byte_0():
    """print_byte(0) prints 00000000"""
    main = (
        'int main(void) {\n'
        '    print_byte(0);\n'
        '}'
    )

    with helpers.replace_main("byte.c", main):
        check50.c.compile("byte.c", lcs50=True)
        check50.run("./byte").stdout("00000000").exit(0)

@check50.check(has_functions)
def test_print_byte_5():
    """print_byte(5) prints 00000101"""
    main = (
        'int main(void) {\n'
        '    print_byte(5);\n'
        '}'
    )

    with helpers.replace_main("byte.c", main):
        check50.c.compile("byte.c", lcs50=True)
        check50.run("./byte").stdout("00000101").exit(0)

@check50.check(has_functions)
def test_print_byte_15():
    """print_byte(15) prints 00001111"""
    main = (
        'int main(void) {\n'
        '    print_byte(15);\n'
        '}'
    )

    with helpers.replace_main("byte.c", main):
        check50.c.compile("byte.c", lcs50=True)
        check50.run("./byte").stdout("00001111").exit(0)

@check50.check(has_functions)
def test_print_byte_254():
    """print_byte(254) prints 11111110"""
    main = (
        'int main(void) {\n'
        '    print_byte(254);\n'
        '}'
    )

    with helpers.replace_main("byte.c", main):
        check50.c.compile("byte.c", lcs50=True)
        check50.run("./byte").stdout("11111110").exit(0)