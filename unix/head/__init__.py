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

# @check50.check(compiles)
# def test_head_head():
#     """./head -10000 head.c prints contents of head.c"""
#     out_real = check50.run("./head -10000 head.c").stdout()
#     out_expected = check50.run("head -10000 head.c").stdout()
#     assert_same(out_expected, out_real)

@check50.check(compiles)
def test_head_head2():
    """./head -2 wordle.txt prints first three lines of worldle.txt"""
    check50.run("echo $'aback\nburnt\ncoyly\ndrawn\nextra' > wordle.txt").exit(0)

    out_real = check50.run("./head -2 wordle.txt").stdout()
    out_expected = "aback\nburnt\n"
    assert_same(out_expected, out_real)

@check50.check(compiles)
def test_head_foo():
    """echo $'hello\\nworld\\nbye' > hello.txt && ./head -2 hello.txt prints: hello\\nworld\\n"""
    check50.run("echo $'hello\nworld\nbye' > hello.txt").exit(0)
    out_real = check50.run("./head -2 hello.txt").stdout()
    out_expected = "hello\nworld\n"
    assert_same(out_expected, out_real)

def assert_same(expected: str, real: str):
    if expected != real:
        msg = f"Expected:\n{expected}\n    But got:\n{real}"
        raise check50.Failure(msg)