import check50
import check50.c


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
    process = check50.run("./conversion").stdin("C").stdin("0").stdin("20").stdin("5")
    check_table(process, "C0205.txt")


@check50.check(compiles)
def testF0102():
    """input of F, 0, 10, 2 yields a well-formatted table"""
    process = check50.run("./conversion").stdin("F").stdin("0").stdin("10").stdin("2")
    check_table(process, "F0102.txt")


@check50.check(compiles)
def testF10003():
    """input of F, 100, 0, 3 yields a well-formatted table"""
    process = check50.run("./conversion").stdin("F").stdin("100").stdin("0").stdin("3")
    check_table(process, "F10003.txt")


@check50.check(compiles)
def testF193():
    """input of F, 1, 9, 3 yields a well-formatted table"""
    process = check50.run("./conversion").stdin("F").stdin("1").stdin("9").stdin("3")
    check_table(process, "F193.txt")


@check50.check(compiles)
def testF093_after_negative():
    """input of v, F, 0, 9, -3, 0, 3 yields a well-formatted table"""
    process = (check50.run("./conversion")
        .stdin("v").stdin("F").stdin("0").stdin("9").stdin("-3").stdin("0").stdin("3"))
    check_table(process, "F093.txt")


def check_table(process, filename):
    # compare the printed table with the expected one, allowing trailing whitespace
    correct = open(filename).read()
    expected = lines(correct)

    out = process.stdout()
    check50.log(f"checking for output \"{correct.strip()}\"...")

    actual = lines(out)
    if not any(actual[i:i + len(expected)] == expected for i in range(len(actual) - len(expected) + 1)):
        raise check50.Mismatch(correct.strip(), out.strip())

    check50.log("checking that program exited with status 0...")
    if process.exitcode != 0:
        raise check50.Failure(f"expected exit code 0, not {process.exitcode}")


def lines(text):
    # split into lines, ignoring trailing whitespace and surrounding blank lines
    return [line.rstrip() for line in text.replace("\r\n", "\n").strip("\n").split("\n")]
