import check50
import check50.c

@check50.check()
def exists():
    """sort.c exists."""
    check50.exists("sort.c")


@check50.check(exists)
def compiles():
    """sort.c compiles."""
    check50.c.compile("sort.c", lcs50=True)


@check50.check(compiles)
def sort_5():
    """sorts 5 numbers"""
    test_sorted(5)


@check50.check(compiles)
def sort_1():
    """sorts 2 numbers"""
    test_sorted(2)


@check50.check(compiles)
def sort_6():
    """sorts 6 numbers"""
    test_sorted(6)


def test_sorted(n_items: int):
    out = check50.run(f"./sort {n_items}").stdout()

    prev_number = float("-inf")

    for i, line in enumerate(out.split("\n")):
        line = line.strip()
        if line:
            try:
                number = int(line)
            except ValueError:
                raise check50.Failure(
                    f"expected a number line on each line of output, but found {line}"
                )
            
            if prev_number > number:
                raise check50.Failure(
                    f"expected each following number to be bigger, but found {prev_number} and {number}"
                )
            
            prev_number = number
