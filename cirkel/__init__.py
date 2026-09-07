import check50
import check50.c

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)
helpers.set_stdout_limit(10000)


CIRKEL5 = """\
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
"""

CIRKEL10 = """\
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
"""


def check_cirkel(stdins, cirkel):
    """Run ./cirkel with stdins and expect cirkel as its output."""
    process = check50.run("./cirkel")

    for line in stdins:
        process.stdin(line)

    helpers.expect_ascii_art(process, cirkel).exit(0)


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
