import check50
import check50.c
import check50.internal

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)

@check50.check()
def exists():
    """strings_more.c exists"""
    check50.exists("strings_more.c")

@check50.check(exists)
def compiles():
    """strings_more.c compiles"""
    check50.c.compile("strings_more.c", lcs50=True)

@check50.check(compiles)
def has_functions():
    """strings_more.c has the functions: is_palindrome and taboo"""
    with open("strings_more.c") as f:
        content = f.read()

    for name in ["is_palindrome", "taboo"]:
        if f" {name}(" not in content:
            raise check50.Failure(f"Missing function: {name}")

@check50.check(has_functions)
def test_is_palindrome_true1():
    """is_palindrome("Never odd or even!") returns true"""
    main = (
        'int main(void) {\n'
        '    printf(is_palindrome("Never odd or even!") ? "true" : "false");\n'
        '}'
    )

    with helpers.replace_main("strings_more.c", main):
        check50.c.compile("strings_more.c", lcs50=True)
        check50.run("./strings_more").stdout("true", regex=False).exit(0)

@check50.check(has_functions)
def test_is_palindrome_true2():
    """is_palindrome("racecar") returns true"""
    main = (
        'int main(void) {\n'
        '    printf(is_palindrome("racecar") ? "true" : "false");\n'
        '}'
    )

    with helpers.replace_main("strings_more.c", main):
        check50.c.compile("strings_more.c", lcs50=True)
        check50.run("./strings_more").stdout("true", regex=False).exit(0)

@check50.check(has_functions)
def test_is_palindrome_false():
    """is_palindrome("true") returns false"""
    main = (
        'int main(void) {\n'
        '    printf(is_palindrome("true") ? "true" : "false");\n'
        '}'
    )

    with helpers.replace_main("strings_more.c", main):
        check50.c.compile("strings_more.c", lcs50=True)
        check50.run("./strings_more").stdout("false", regex=False).exit(0)

@check50.check(has_functions)
def test_taboo():
    """taboo("The Cheshire Cat is the cat of the Duchess.") prints The Cheshire Dog is the dog of the Duchess."""
    main = (
        'int main(void) {\n'
        '    taboo("The Cheshire Cat is the cat of the Duchess.");\n'
        '}'
    )

    with helpers.replace_main("strings_more.c", main):
        check50.c.compile("strings_more.c", lcs50=True)
        check50.run("./strings_more").stdout("The Cheshire Dog is the dog of the Duchess.", regex=False).exit(0)
