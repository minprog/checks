import check50
import check50.c
import check50.internal

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../../helpers/helpers.py"
)
helpers.set_stdout_limit(100000)

@check50.check()
def exists():
    """nl.c exists"""
    check50.exists("nl.c")

@check50.check(exists)
def compiles():
    """nl.c compiles"""
    check50.c.compile("nl.c", lcs50=True)

@check50.check(compiles)
def test_nl_nl():
    """./nl nl.c prints the exact same as: nl nl.c"""
    out_real = check50.run("./nl nl.c").stdout()
    out_expected = check50.run("nl nl.c").stdout()

    # Mac's nl uses \t in other places than Linux's nl
    out_real = out_real.replace("\t", " ")
    out_expected = out_expected.replace("\t", " ")

    assert_same(out_expected, out_real)

@check50.check(compiles)
def test_nl_foo():
    """echo "hello\\nworld\\n" > foo.c && ./nl foo.c prints the exact same as: nl foo.c"""
    check50.run('echo "hello\nworld\n" > foo.c').exit(0)
    out_real = check50.run("./nl foo.c").stdout()
    out_expected = check50.run("nl foo.c").stdout()

    # Mac's nl uses \t in other places than Linux's nl
    out_real = out_real.replace("\t", " ")
    out_expected = out_expected.replace("\t", " ")

    assert_same(out_expected, out_real)

def assert_same(expected: str, real: str):
    if expected != real:
        msg = f"Expected:\n{expected}\n    But got:\n{real}"
        raise check50.Failure(msg)
