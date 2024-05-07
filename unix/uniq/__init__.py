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
def test_uniq_fruit():
    """echo $'ananas\\nananas\\nbanaan\\nwortel\\nbanaan\\nbanaan' > fruit.txt && ./uniq fruit.txt prints: ananas\\nbanaan\\nwortel\\nbanaan\\n"""
    check50.run("echo $'ananas\nananas\nbanaan\nwortel\nbanaan\nbanaan' > fruit.txt").exit(0)
    out_real = check50.run("./uniq fruit.txt").stdout()
    out_expected = "ananas\nbanaan\nwortel\nbanaan\n"
    assert_same(out_expected, out_real)

@check50.check(compiles)
def test_uniq_boodschappen():
    """echo $'brood\\nkaas' > boodschappen.txt && ./uniq boodschappen.txt prints: brood\\nkaas\\n"""
    check50.run("echo $'brood\nkaas' > boodschappen.txt").exit(0)
    out_real = check50.run("./uniq boodschappen.txt").stdout()
    out_expected = "brood\nkaas\n"
    assert_same(out_expected, out_real)

def assert_same(expected: str, real: str):
    if expected != real:
        print_expected = helpers.encode_unprintable(expected)
        print_real = helpers.encode_unprintable(real)
        if len(print_real) > len(print_expected) + 15:
            print_real = print_real[:len(print_expected)+15] + " ..."
        msg = f"Expected:\n{print_expected}\n    But got:\n{print_real}"
        raise check50.Failure(msg)
