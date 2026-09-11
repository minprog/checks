import check50
import check50.c

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)
helpers.set_stdout_limit(1000)


def check_tabel(stdins, filename):
    """Run ./conversion with stdins and expect the table in filename as its output."""
    process = check50.run("./conversion")

    for line in stdins:
        process.stdin(line)

    expected = open(filename).read()
    helpers.expect_ascii_art(process, expected, "de tabel is niet zoals verwacht").exit(0)


@check50.check()
def exists():
    """conversion.c exists"""
    check50.exists("conversion.c")
    check50.include("C0205.txt", "F0102.txt", "F10003.txt", "F193.txt", "F093.txt")


@check50.check(exists)
def compiles():
    """conversion.c compiles"""
    check50.c.compile("conversion.c", lcs50=True)


@check50.check(compiles)
def testC0205():
    """input of C, 0, 20, 5 yields a well-formatted table"""
    check_tabel(["C", "0", "20", "5"], "C0205.txt")


@check50.check(compiles)
def testF0102():
    """input of F, 0, 10, 2 yields a well-formatted table"""
    check_tabel(["F", "0", "10", "2"], "F0102.txt")


@check50.check(compiles)
def testF10003():
    """input of F, 100, 0, 3 yields a well-formatted table"""
    check_tabel(["F", "100", "0", "3"], "F10003.txt")


@check50.check(compiles)
def testF193():
    """input of F, 1, 9, 3 yields a well-formatted table"""
    check_tabel(["F", "1", "9", "3"], "F193.txt")


@check50.check(compiles)
def testF093_after_negative():
    """input of v, F, 0, 9, -3, 0, 3 yields a well-formatted table"""
    check_tabel(["v", "F", "0", "9", "-3", "0", "3"], "F093.txt")
