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
    """uniq.c exists"""
    check50.exists("uniq.c")

@check50.check(exists)
def compiles():
    """uniq.c compiles"""
    check50.c.compile("uniq.c", lcs50=True)

@check50.check(compiles)
def test_uniq_foo():
    """echo $'ananas\\nananas\\nbanaan\\nwortel\\nbanaan\\nbanaan' > fruit.txt && ./uniq fruit.txt prints: ananas\\nbanaan\\nwortel\\nbanaan\\n"""
    check50.run("echo $'ananas\nananas\nbanaan\nwortel\nbanaan\nbanaan' > fruit.txt").exit(0)
    out_real = check50.run("./uniq fruit.txt").stdout()
    out_expected = "ananas\nbanaan\nwortel\nbanaan\n"
    assert_same(out_expected, out_real)

# @check50.check(compiles)
# def test_uniq_uniq():
#     """./uniq uniq.c prints unique contents of uniq.c"""
#     out_real = check50.run("./uniq uniq.c").stdout()
#     out_expected = check50.run("uniq uniq.c").stdout()
#     assert_same(out_expected, out_real)

def assert_same(expected: str, real: str):
    if expected != real:
        msg = f"Expected:\n{expected}\n    But got:\n{real}"
        raise check50.Failure(msg)