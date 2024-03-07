import check50
import check50.c
import check50.internal

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../../helpers/helpers.py"
)
helpers.set_stdout_limit(10000)

@check50.check()
def exists():
    """cat.c exists"""
    check50.exists("cat.c")

@check50.check(exists)
def compiles():
    """cat.c compiles"""
    check50.c.compile("cat.c", lcs50=True)

@check50.check(compiles)
def test_cat_cat():
    """./cat cat.c prints contents of cat.c"""
    out_real = check50.run("./cat cat.c").stdout()
    out_expected = check50.run("cat cat.c").stdout()

    assert_same(out_expected, out_real)

@check50.check(compiles)
def test_cat_foo():
    """echo $'hello\\nworld' > hello.txt && ./cat hello.txt prints all text, including final newline if present"""
    check50.run("echo $'hello\nworld' > hello.txt").exit(0)
    out_real = check50.run("./cat hello.txt").stdout()
    out_expected = "hello\nworld\n"
    assert_same(out_expected, out_real)

def assert_same(expected: str, real: str):
    if expected != real:
        msg = f"Expected:\n{expected}\n    But got:\n{real}"
        raise check50.Failure(msg)
