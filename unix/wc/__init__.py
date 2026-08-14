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
    """wc.c exists"""
    check50.exists("wc.c")

@check50.check(exists)
def compiles():
    """wc.c compiles"""
    check50.c.compile("wc.c", lcs50=True)

@check50.check(compiles)
def test_wc_foo():
    """echo $'hello\\nworld' > hello.txt && ./wc hello.txt prints 2 2 12 hello.txt"""
    check50.run("echo $'hello\nworld' > hello.txt").exit(0)

    out_real = check50.run("./wc hello.txt").stdout()
    out_expected = "       2       2      12 hello.txt\n"

    # wc uses different whitespace on Mac/Linux, so the exact spacing between
    # the columns is free: only the counts and the filename have to match
    assert_same_words(out_expected, out_real)

# @check50.check(compiles)
# def test_wc_wc():
#     """./wc wc.c prints the exact same as: wc wc.c"""
#     # wc uses different whitespaces on Mac/Linux
#     out_real = " ".join(check50.run("./wc wc.c").stdout().split())
#     out_expected = " ".join(check50.run("wc wc.c").stdout().split())
#     assert_same(out_expected, out_real)

def assert_same(expected: str, real: str):
    if expected != real:
        msg = f"Expected:\n{expected}\n    But got:\n{real}"
        raise check50.Failure(msg)

def assert_same_words(expected: str, real: str):
    """Compare the words, ignoring how much whitespace is used between them"""
    if expected.split() != real.split():
        msg = f"Expected:\n{expected}\n    But got:\n{real}"
        raise check50.Failure(msg)
