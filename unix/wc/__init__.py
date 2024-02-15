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
def test_wc_wc():
    """./wc wc.c prints the exact same as: wc wc.c"""
    # wc uses different whitespaces on Mac/Linux
    out_real = " ".join(check50.run("./wc wc.c").stdout().split())
    out_expected = " ".join(check50.run("wc wc.c").stdout().split())
    assert_same(out_expected, out_real)

@check50.check(compiles)
def test_wc_foo():
    """echo "hello\\nworld\\n" > foo.c && ./wc foo.c prints the exact same as: wc foo.c"""
    check50.run('echo "hello\nworld\n" > foo.c').exit(0)

    # wc uses different whitespaces on Mac/Linux
    out_real = " ".join(check50.run("./wc foo.c").stdout().split())
    out_expected = " ".join(check50.run("wc foo.c").stdout().split())
    assert_same(out_expected, out_real)

def assert_same(expected: str, real: str):
    if expected != real:
        msg = f"Expected:\n{expected}\n    But got:\n{real}"
        raise check50.Failure(msg)