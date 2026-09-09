import re

import check50
import check50.c
import check50.internal

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)
helpers.set_stdout_limit(10000)


@check50.check()
def exists():
    """caffeine.c exists"""
    check50.exists("caffeine.c")


@check50.check(exists)
def compiles():
    """caffeine.c compiles"""
    check50.c.compile("caffeine.c", lcs50=True)


@check50.check(compiles)
def test010():
    """input of 0.10 yields output of 2 drinks"""
    check50.run("./caffeine").stdin("0.10").stdout(number(1), "1\n").stdout(number(1), "4\n").stdout(number(2), "2\n").exit(0)


@check50.check(compiles)
def test001():
    """input of 0.01 yields output of 1 drink"""
    process = check50.run("./caffeine").stdin("0.01")
    check_total(process, 1)


@check50.check(compiles)
def test0001():
    """input of 0.001 yields output of 0 drinks"""
    process = check50.run("./caffeine").stdin("0.001")
    check_total(process, 0)


@check50.check(compiles)
def test025():
    """input of 0.25 yields output of 5 drinks"""
    check50.run("./caffeine").stdin("0.25").stdout(number(3), "3\n").stdout(number(1), "1\n").stdout(number(1), "1\n").stdout(number(5), "5\n").exit(0)


@check50.check(compiles)
def test0251():
    """input of 0.251 yields, among other things, a piece of chocolate"""
    check50.run("./caffeine").stdin("0.251").stdout(number(3), "3\n").stdout(number(1), "1\n").stdout(number(1), "1\n").stdout(number(1), "1\n").stdout(number(5), "5\n").exit(0)

@check50.check(compiles)
def test_reject_negative():
    """rejects a negative input like -1"""
    check50.run("./caffeine").stdin("-1").reject()


@check50.check(test_reject_negative)
def test_025_after_negative():
    """erroneous input of -1 and then input of 0.25 yields output of 5"""
    check50.run("./caffeine").stdin("-1").stdin("0.25").stdout(number(3), "3\n").stdout(number(1), "1\n").stdout(number(1), "1\n").stdout(number(5), "5\n").exit(0)


@check50.check(compiles)
def test_reject_foo():
    """rejects a non-numeric input of "foo" """
    check50.run("./caffeine").stdin("foo").reject()


@check50.check(compiles)
def test_reject_empty():
    """rejects a non-numeric input of "" """
    check50.run("./caffeine").stdin("").reject()


def number(num):
    # regex that matches `num` not surrounded by any other numbers (so number(2) won't match e.g. 123)
    return fr"(?<!\d){num}(?!\d)"


def check_total(process, num):
    # check the final total, with explicit feedback when only the pluralization is wrong
    expected_word = "drink" if num == 1 else "drinks"
    wrong_word = "drinks" if num == 1 else "drink"
    expected = f"That makes {num} {expected_word} in total"

    out = process.stdout()
    check50.log(f'checking for output "{expected}"...')

    if re.search(fr"(?<!\d){num}(?!\d)\s+{wrong_word}\b", out):
        raise check50.Failure(
            f'expected "{num} {expected_word}", not "{num} {wrong_word}"',
            help='this is about the pluralization of the word "drink": use "drink" '
                 'for exactly 1 drink and "drinks" for any other number, so the last '
                 f'line should read "{expected}"')

    if not re.search(fr"(?<!\d){num}(?!\d)\s+{expected_word}\b", out):
        raise check50.Mismatch(expected, out.strip())

    check50.log("checking that program exited with status 0...")
    if process.exitcode != 0:
        raise check50.Failure(f"expected exit code 0, not {process.exitcode}")
