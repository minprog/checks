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
    """paste.c exists"""
    check50.exists("paste.c")

@check50.check(exists)
def compiles():
    """paste.c compiles"""
    check50.c.compile("paste.c", lcs50=True)

@check50.check(compiles)
def test_paste_foo_bar():
    """echo $'a\\nb\\nc' > foo.txt && echo $'d\\ne' > bar.txt && ./paste foo.txt bar.txt prints: a,d\\nb,e\\nc,\\n"""
    check50.run("echo $'a\nb\nc' > foo.txt").exit(0)
    check50.run("echo $'d\ne' > bar.txt").exit(0)
    out_real = check50.run("./paste foo.txt bar.txt").stdout()
    out_expected = check50.run("paste -d , foo.txt bar.txt").stdout()
    assert_same(out_expected, out_real)

@check50.check(compiles)
def test_paste_cut():
    """echo $'a\\nb\\nc' > foo.txt && ./paste foo.txt foo.txt | cut -f1 -d , prints the contents of foo.txt"""
    check50.run("echo $'a\nb\nc' > foo.txt").exit(0)
    out_real = check50.run("./paste foo.txt foo.txt | cut -f1 -d ,").stdout()
    out_expected = check50.run("paste -d , foo.txt foo.txt | cut -f1 -d ,").stdout()
    assert_same(out_expected.strip(), out_real.strip())

def assert_same(expected: str, real: str):
    if expected != real:
        msg = f"Expected:\n{expected}\n    But got:\n{real}"
        raise check50.Failure(msg)