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
    """nl.c exists"""
    check50.exists("nl.c")

@check50.check(exists)
def compiles():
    """nl.c compiles"""
    check50.c.compile("nl.c", lcs50=True)

@check50.check(compiles)
def test_nl_foo():
    """echo $'hello\\nworld' > hello.txt && ./nl hello.txt prints the file with line numbers"""
    check50.run("echo $'hello\nworld' > hello.txt").exit(0)

    out_real = check50.run("./nl hello.txt").stdout()
    out_expected = "      1 hello\n      2 world\n"

    assert_same(out_expected, out_real)

@check50.check(compiles)
def test_nl_nl():
    """echo $'hello\\n\\nworld' > hello.txt && ./nl hello.txt skips the blank line"""
    check50.run("echo $'hello\n\nworld' > hello.txt").exit(0)

    out_real = check50.run("./nl hello.txt").stdout()
    out_expected = "      1 hello\n\n      2 world\n"

    assert_same(out_expected, out_real)

def remove_whitespace_from_empty_lines(text: str):
    return "\n".join(line if line.strip() != "" else line.strip() for line in text.split("\n"))

def assert_same(expected: str, real: str):
    if expected != real:
        msg = f"Expected:\n{expected}\n    But got:\n{real}"
        raise check50.Failure(msg)
