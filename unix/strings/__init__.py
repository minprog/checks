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
    """strings.c exists"""
    check50.exists("strings.c")

@check50.check(exists)
def compiles():
    """strings.c compiles"""
    check50.c.compile("strings.c", lcs50=True)

@check50.check(compiles)
def test_strings_foo():
    """echo $'hello\\nworld\\nbye' > foo.txt && ./strings foo.txt prints: hello\\nworld\\nbye\\n"""
    check50.run("echo $'hello\nworld\nbye' > foo.txt").exit(0)
    out_real = check50.run("./strings foo.txt").stdout()
    out_expected = "hello\nworld\nbye\n"
    assert_same(out_expected, out_real)

@check50.check(compiles)
def test_strings_strings():
    """echo $'ABCD\\x00ABCD\\x00BD\\x00' > foo.txt && ./strings foo.txt prints: ABCD\\nABCD\\n"""
    with open("foo.txt", "wb") as f:
        f.write(bytes([65, 66, 67, 68, 0, 65, 66, 67, 68, 0, 66, 68, 0]))
    out_real = check50.run("./strings foo.txt").stdout()
    out_expected = "ABCD\nABCD\n"
    assert_same(out_expected, out_real)

def assert_same(expected: str, real: str):
    if expected != real:
        msg = f"Expected:\n{expected}\n    But got:\n{real}"
        raise check50.Failure(msg)
