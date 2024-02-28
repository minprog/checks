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
    """head.c exists"""
    check50.exists("head.c")

@check50.check(exists)
def compiles():
    """head.c compiles"""
    check50.c.compile("head.c", lcs50=True)

@check50.check(compiles)
def test_head_head():
    """./head -10000 head.c prints contents of head.c"""
    out_real = check50.run("./head -10000 head.c").stdout()
    out_expected = check50.run("head -10000 head.c").stdout()
    assert_same(out_expected, out_real)

@check50.check(compiles)
def test_head_head3():
    """./head -3 head.c prints first three lines of head.c"""
    out_real = check50.run("./head -3 head.c").stdout()
    out_expected = check50.run("head -3 head.c").stdout()
    assert_same(out_expected, out_real)

@check50.check(compiles)
def test_head_foo():
    """echo $'hello\\nworld\\nbye\\n' > foo.c && ./head -2 foo.c prints: hello\\nworld\\n"""
    check50.run("echo $'hello\nworld\nbye\n' > foo.c").exit(0)
    out_real = check50.run("./head -2 foo.c").stdout()
    out_expected = check50.run("head -2 foo.c").stdout()
    assert_same(out_expected, out_real)

def assert_same(expected: str, real: str):
    if expected != real:
        msg = f"Expected:\n{expected}\n    But got:\n{real}"
        raise check50.Failure(msg)