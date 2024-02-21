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
    """tail.c exists"""
    check50.exists("tail.c")

@check50.check(exists)
def compiles():
    """tail.c compiles"""
    check50.c.compile("tail.c", lcs50=True)

@check50.check(compiles)
def test_tail_tail():
    """./tail -10000 tail.c prints contents of tail.c"""
    out_real = check50.run("./tail -10000 tail.c").stdout()
    out_expected = check50.run("tail -10000 tail.c").stdout()
    assert_same(out_expected, out_real)

@check50.check(compiles)
def test_tail_tail3():
    """./tail -3 tail.c prints last three lines of tail.c"""
    out_real = check50.run("./tail -3 tail.c").stdout()
    out_expected = check50.run("tail -3 tail.c").stdout()
    assert_same(out_expected, out_real)

@check50.check(compiles)
def test_tail_foo():
    """echo "hello\\nworld\\nbye\\n" > foo.c && ./tail -2 foo.c prints: world\\nbye\\n"""
    check50.run('echo "hello\nworld\nbye\n" > foo.c').exit(0)
    out_real = check50.run("./tail -2 foo.c").stdout()
    out_expected = check50.run("tail -2 foo.c").stdout()
    assert_same(out_expected, out_real)

def assert_same(expected: str, real: str):
    if expected != real:
        msg = f"Expected:\n{expected}\n    But got:\n{real}"
        raise check50.Failure(msg)