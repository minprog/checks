import re

import check50
import check50.c

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)
helpers.set_stdout_limit(10000)


CIRKEL5 = """
   xxxxx
  x     x
 x       x
x         x
x         x
x         x
x         x
x         x
 x       x
  x     x
   xxxxx
"""[1:]

CIRKEL10 = """
       xxxxxxx
     xx       xx
    x           x
   x             x
  x               x
 x                 x
 x                 x
x                   x
x                   x
x                   x
x                   x
x                   x
x                   x
x                   x
 x                 x
 x                 x
  x               x
   x             x
    x           x
     xx       xx
       xxxxxxx
"""[1:]


def to_regex(cirkel):
    """Turn a circle into a regex that ignores trailing whitespace per line."""
    return "".join(re.escape(line) + r"\s*\n" for line in cirkel.splitlines())


def side_by_side(expected, actual):
    """Render expected and actual output next to each other, line by line."""
    expected_lines = expected.splitlines()
    actual_lines = [line.rstrip() for line in actual.replace("\r\n", "\n").splitlines()]

    header_expected, header_actual = "verwacht:", "jouw uitvoer:"
    width = max([len(line) for line in expected_lines] + [len(header_expected)])

    lines = [f"{header_expected.ljust(width)}   {header_actual}"]
    lines.append(f"{'-' * width}   {'-' * len(header_actual)}")

    for i in range(max(len(expected_lines), len(actual_lines))):
        left = expected_lines[i] if i < len(expected_lines) else ""
        right = actual_lines[i] if i < len(actual_lines) else ""
        marker = "  " if left == right else "<>"
        lines.append(f"{left.ljust(width)} {marker}{right}")

    return "\n".join(lines)


def check_cirkel(stdins, cirkel):
    """Run ./cirkel with stdins, expect cirkel as output, and report readably."""
    process = check50.run("./cirkel")

    for line in stdins:
        process.stdin(line)

    try:
        process.stdout(to_regex(cirkel), str_output=cirkel).exit(0)
    except check50.Mismatch as error:
        actual = error.payload["actual"]
    except check50.Missing as error:
        actual = error.payload["collection"]
    else:
        return

    raise check50.Failure(
        "de uitvoer is niet zoals verwacht",
        help=side_by_side(cirkel, actual)
    )


@check50.check()
def exists():
    """cirkel.c exists"""
    check50.exists("cirkel.c")


@check50.check(exists)
def compiles():
    """cirkel.c compiles"""
    check50.c.compile("cirkel.c", lcs50=True)


@check50.check(compiles)
def test_cirkel5():
    """cirkel met hoogte 5 is correct"""
    check_cirkel(["5"], CIRKEL5)


@check50.check(compiles)
def test_cirkel10():
    """cirkel met hoogte 10 is correct"""
    check_cirkel(["10"], CIRKEL10)


@check50.check(compiles)
def test_cirkel_incorrect_input():
    """vraagt opnieuw om input bij een incorrecte hoogte van 3"""
    check_cirkel(["3", "5"], CIRKEL5)
