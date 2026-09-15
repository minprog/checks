import check50
import check50.c
import check50.internal

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)
helpers.set_stdout_limit(100)

@check50.check()
def exists():
    """strings.c exists"""
    check50.exists("strings.c")

@check50.check(exists)
def compiles():
    """strings.c compiles"""
    check50.c.compile("strings.c", lcs50=True)

@check50.check(compiles)
def has_functions():
    """strings.c has the functions: vertical, skip, eek, first_last, bob, and has_duplicate"""
    with open("strings.c") as f:
        content = f.read()

    for name in ["vertical", "skip", "eek", "first_last", "bob", "has_duplicate"]:
        if not helpers.has_function(content, name):
            raise check50.Failure(f"Missing function: {name}")

@check50.check(has_functions)
def test_vertical():
    """vertical("horizontal") prints h\\no\\nr\\ni\\nz\\no\\nn\\nt\\na\\nl\\n"""
    main = (
        'int main(void) {\n'
        '    vertical("horizontal");\n'
        '}'
    )

    with helpers.replace_main("strings.c", main):
        check50.c.compile("strings.c", lcs50=True)
        check50.run("./strings").stdout("h\no\nr\ni\nz\no\nn\nt\na\nl\n", regex=False).exit(0)

@check50.check(has_functions)
def test_skip():
    """skip("Great, gifts!") prints Get it!"""
    main = (
        'int main(void) {\n'
        '    skip("Great, gifts!");\n'
        '}'
    )

    with helpers.replace_main("strings.c", main):
        check50.c.compile("strings.c", lcs50=True)
        check50.run("./strings").stdout("Get it!", regex=False).exit(0)

@check50.check(has_functions)
def test_eek():
    """eek("Eek, a mouse!") prints The text "Eek, a mouse!" contains 3 e's."""
    main = (
        'int main(void) {\n'
        '    eek("Eek, a mouse!");\n'
        '}'
    )

    with helpers.replace_main("strings.c", main):
        check50.c.compile("strings.c", lcs50=True)
        check50.run("./strings").stdout("The text \"Eek, a mouse!\" contains 3 e's", regex=False).exit(0)

@check50.check(has_functions)
def test_first_last():
    """first_last("tokyo hotel") prints First: t\\nLast: l\\n"""
    main = (
        'int main(void) {\n'
        '    first_last("tokyo hotel");\n'
        '}'
    )

    with helpers.replace_main("strings.c", main):
        check50.c.compile("strings.c", lcs50=True)
        check50.run("./strings").stdout("First: t\nLast: l\n", regex=False).exit(0)

@check50.check(has_functions)
def test_first_last_single():
    """first_last("x") prints First: x\\nLast: x\\n"""
    main = (
        'int main(void) {\n'
        '    first_last("x");\n'
        '}'
    )

    with helpers.replace_main("strings.c", main):
        check50.c.compile("strings.c", lcs50=True)
        check50.run("./strings").stdout("First: x\nLast: x\n", regex=False).exit(0)

@check50.check(has_functions)
def test_bob_no_modification():
    """bob does >>not<< modify the string"""
    main = (
        'int main(void) {\n'
        '    char original[] = "Know your meme";\n'
        '    bob(original);\n'
        '    printf("%s should be Know your meme\\n", original);\n'
        '}'
    )

    with helpers.replace_main("strings.c", main):
        check50.c.compile("strings.c", lcs50=True)
        check50.run("./strings").stdout("Know your meme should be Know your meme", regex=False).exit(0)

@check50.check(test_bob_no_modification)
def test_bob():
    """bob("Know your meme") prints kNoW YoUr mEmE"""
    main = (
        'int main(void) {\n'
        '    bob("Know your meme");\n'
        '}'
    )

    with helpers.replace_main("strings.c", main):
        check50.c.compile("strings.c", lcs50=True)
        try:
            check50.run("./strings").stdout("kNoW yOuR mEmE", regex=False).exit(0)
        # also accept kNoW YoUr mEmE
        except check50.Failure:
            check50.run("./strings").stdout("kNoW YoUr mEmE", regex=False).exit(0)

@check50.check(has_functions)
def test_has_duplicate_true():
    """has_duplicate("tokyo") returns true"""
    main = (
        'int main(void) {\n'
        '    printf("%s\\n", has_duplicate("tokyo") ? "true" : "false");\n'
        '}'
    )

    with helpers.replace_main("strings.c", main):
        check50.c.compile("strings.c", lcs50=True)
        check50.run("./strings").stdout("true\n", regex=False).exit(0)

@check50.check(has_functions)
def test_has_duplicate_false():
    """has_duplicate("hotel") returns false"""
    main = (
        'int main(void) {\n'
        '    printf("%s\\n", has_duplicate("hotel") ? "true" : "false");\n'
        '}'
    )

    with helpers.replace_main("strings.c", main):
        check50.c.compile("strings.c", lcs50=True)
        check50.run("./strings").stdout("false\n", regex=False).exit(0)

@check50.check(has_functions)
def test_has_duplicate_first_last():
    """has_duplicate("abcda") returns true"""
    main = (
        'int main(void) {\n'
        '    printf("%s\\n", has_duplicate("abcda") ? "true" : "false");\n'
        '}'
    )

    with helpers.replace_main("strings.c", main):
        check50.c.compile("strings.c", lcs50=True)
        check50.run("./strings").stdout("true\n", regex=False).exit(0)

@check50.check(has_functions)
def test_has_duplicate_single():
    """has_duplicate("x") returns false"""
    main = (
        'int main(void) {\n'
        '    printf("%s\\n", has_duplicate("x") ? "true" : "false");\n'
        '}'
    )

    with helpers.replace_main("strings.c", main):
        check50.c.compile("strings.c", lcs50=True)
        check50.run("./strings").stdout("false\n", regex=False).exit(0)
