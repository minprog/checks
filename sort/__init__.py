import check50
import check50.c

@check50.check()
def exists():
    """helpers.c exists."""
    check50.exists("helpers.c")


@check50.check(exists)
def compiles():
    """helpers.c compiles."""
    check50.include("helpers.h", "sort.c")
    check50.c.compile("sort.c", "helpers.c", exe_name="sort", lcs50=True)


@check50.check(compiles)
def sort_2():
    """sorts 2 numbers"""
    # two random numbers are already in order half of the time, so repeat
    for _ in range(12):
        test_sorted(2)


@check50.check(compiles)
def sort_5():
    """sorts 5 numbers"""
    test_sorted(5)


@check50.check(compiles)
def sort_6():
    """sorts 6 numbers"""
    test_sorted(6)


def test_sorted(n_items: int):
    out = check50.run(f"./sort {n_items}").stdout()

    numbers = []
    for line in out.split("\n"):
        line = line.strip()
        if not line:
            continue

        try:
            numbers.append(int(line))
        except ValueError:
            raise check50.Failure(f"expected a number on each line of output, but found {line}")

    if len(numbers) != n_items:
        raise check50.Failure(f"expected {n_items} numbers, but found {len(numbers)}")

    for prev, number in zip(numbers, numbers[1:]):
        if prev > number:
            raise check50.Failure(f"expected each following number to be bigger, but found {prev} and {number}")
