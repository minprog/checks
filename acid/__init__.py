import check50
import check50.c
import check50.internal

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)

@check50.check()
def exists():
    """acid.c exists"""
    check50.exists("acid.c")

@check50.check(exists)
def compiles():
    """acid.c compiles"""
    check50.c.compile("acid.c", lcs50=True)

@check50.check(compiles)
def has_functions():
    """acid.c has the function is_acidic"""
    with open("acid.c") as f:
        content = f.read()

    for name in ["is_acidic"]:
        if f" {name}(" not in content:
            raise check50.Failure(f"Missing function: {name}")

@check50.check(has_functions)
def no_print_in_is_acidic():
    """the function is_acidic does not print output"""
    main = (
        'int main(void) {\n'
        '    is_acidic(5.0);\n'
        '}'
    )

    with helpers.replace_main("acid.c", main):
        check50.c.compile("acid.c", lcs50=True)
        stdout = check50.run("./acid").stdout()
        if len(stdout) != 0:
            raise check50.Failure("Make sure is_acidic only returns the result. In other words, don't use printf.")


@check50.check(no_print_in_is_acidic)
def test_is_acidic_yes():
    """is_acidic(2.5) returns true"""
    main = (
        'int main(void) {\n'
        '    printf("%s", is_acidic(2.5) ? "true" : "false");\n'
        '}'
    )

    with helpers.replace_main("acid.c", main):
        check50.c.compile("acid.c", lcs50=True)
        check50.run("./acid").stdout("true").exit(0)

@check50.check(no_print_in_is_acidic)
def test_is_acidic_no():
    """is_acidic(8.5) returns false"""
    main = (
        'int main(void) {\n'
        '    printf("%s", is_acidic(8.5) ? "true" : "false");\n'
        '}'
    )

    with helpers.replace_main("acid.c", main):
        check50.c.compile("acid.c", lcs50=True)
        check50.run("./acid").stdout("false").exit(0)

@check50.check(no_print_in_is_acidic)
def test_is_acidic_edgecase():
    """is_acidic(7.0) returns false"""
    main = (
        'int main(void) {\n'
        '    printf("%s", is_acidic(7.0) ? "true" : "false");\n'
        '}'
    )

    with helpers.replace_main("acid.c", main):
        check50.c.compile("acid.c", lcs50=True)
        check50.run("./acid").stdout("false").exit(0)

@check50.check(test_is_acidic_edgecase)
def test_program():
    """the program takes in user input and prints a message"""
    stdout = check50.run("./acid").stdin("7.0").stdout()
    if len(stdout) == 0:
        check50.Failure("Be sure to print out a message to the user whether the PH is acidic or not.")