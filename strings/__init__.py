import check50
import check50.c
import check50.internal

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)

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
    """strings.c has the functions vertical, skip, eek, and bob"""
    with open("strings.c") as f:
        content = f.read()

    for name in ["vertical", "skip", "eek", "bob"]:
        if f" {name}(" not in content:
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
def test_bob():
    """bob("Know your meme") prints Spongebob says: kNoW yOuR mEmE"""
    main = (
        'int main(void) {\n'
        '    bob("Know your meme");\n'
        '}'
    )

    with helpers.replace_main("strings.c", main):
        check50.c.compile("strings.c", lcs50=True)
        check50.run("./strings").stdout("Spongebob says: kNoW yOuR mEmE", regex=False).exit(0)
