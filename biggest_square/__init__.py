import random

import check50
import check50.c
import check50.internal

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)
helpers.set_stdout_limit(10000)


EXAMPLE = """\
...........................
....o......................
............o..............
...........................
....o......................
...............o...........
...........................
......o..............o.....
..o.......o................
"""


@check50.check()
def exists():
    """biggest_square.c exists"""
    check50.exists("biggest_square.c")


@check50.check(exists)
def compiles():
    """biggest_square.c compiles"""
    check50.c.compile("biggest_square.c", lcs50=True)


@check50.check(compiles)
def usage():
    """zonder of met te veel argumenten print: Usage: ./biggest_square <kaart>"""
    for command in ["./biggest_square", "./biggest_square map.txt map.txt"]:
        with open("map.txt", "w") as f:
            f.write(".\n")
        process = check50.run(command)
        output = process.stdout().strip()
        if output != "Usage: ./biggest_square <kaart>":
            raise check50.Failure(f"verwachtte Usage: ./biggest_square <kaart> bij {command}, maar kreeg {output}")
        if process.exitcode != 1:
            raise check50.Failure(f"verwachtte exit code 1 bij {command}, niet {process.exitcode}")


@check50.check(compiles)
def missing_file():
    """een bestand dat niet bestaat geeft map error"""
    process = check50.run("./biggest_square bestaat_niet.txt")
    output = process.stdout().strip()
    if output != "map error":
        raise check50.Failure(f"verwachtte alleen \"map error\" als uitvoer, maar kreeg {output}")
    if process.exitcode != 1:
        raise check50.Failure(f"verwachtte exit code 1, niet {process.exitcode}")


@check50.check(compiles)
def example():
    """de voorbeeldkaart uit de opdracht geeft het juiste vierkant"""
    expect_solution(EXAMPLE)


@check50.check(compiles)
def single_cell():
    """een kaart van één leeg vakje wordt helemaal vol"""
    expect_solution(".\n")


@check50.check(compiles)
def no_space():
    """een kaart met alleen obstakels blijft ongewijzigd"""
    expect_solution("ooo\nooo\nooo\n")


@check50.check(compiles)
def tie_top():
    """bij twee even grote vierkanten wordt het hoogste gekozen"""
    expect_solution(
        "o..oo\n"
        "o..oo\n"
        "ooooo\n"
        "oo..o\n"
        "oo..o\n"
    )


@check50.check(compiles)
def tie_left():
    """bij twee even hoge vierkanten wordt het meest linkse gekozen"""
    expect_solution(
        "oooo..o..\n"
        "o..o..o..\n"
        "o..oooooo\n"
    )


@check50.check(compiles)
def rectangular():
    """werkt ook op kaarten die hoger dan breed zijn"""
    expect_solution(
        "...\n"
        ".o.\n"
        "...\n"
        "...\n"
        "...\n"
        "o..\n"
    )


@check50.check(compiles)
def large():
    """vindt het juiste vierkant op grote willekeurige kaarten van 100 bij 100"""
    rng = random.Random(42)
    for density in (2, 5, 10):
        rows = ["".join("o" if rng.randrange(100) < density else "." for _ in range(100))
                for _ in range(100)]
        expect_solution("\n".join(rows) + "\n", timeout=10)


@check50.check(compiles)
def max_size():
    """een kaart van precies 100 regels van 100 tekens is geldig"""
    expect_solution(("." * 100 + "\n") * 100)


@check50.check(compiles)
def too_many_lines():
    """een kaart met meer dan 100 regels geeft map error"""
    expect_error(("..." + "\n") * 101)


@check50.check(compiles)
def too_wide():
    """een kaart met regels langer dan 100 tekens geeft map error"""
    expect_error(("." * 101 + "\n") * 3)


@check50.check(compiles)
def unequal_lines():
    """een kaart met regels van verschillende lengte geeft map error"""
    expect_error("...\n....\n...\n")


@check50.check(compiles)
def empty_line():
    """een kaart met een lege regel geeft map error"""
    expect_error("...\n\n...\n")


@check50.check(compiles)
def unknown_character():
    """een kaart met een onbekend teken geeft map error"""
    expect_error("...\n.a.\n...\n")


@check50.check(compiles)
def full_character_in_map():
    """een kaart waarin al een x staat geeft map error"""
    expect_error("...\n.x.\n...\n")


@check50.check(compiles)
def empty_input():
    """een leeg bestand geeft map error"""
    expect_error("")


# helpers --------------------------------------------------------------------

def solve(text):
    """Return the expected output for a valid map"""
    rows = text.splitlines()
    empty, full = ".", "x"
    height, width = len(rows), len(rows[0])

    # sizes[r][c] is the size of the largest square with its bottom-right corner at (r, c)
    sizes = [[0] * (width + 1) for _ in range(height + 1)]
    best, best_r, best_c = 0, 0, 0
    for r in range(height):
        for c in range(width):
            if rows[r][c] == empty:
                size = 1 + min(sizes[r][c], sizes[r][c + 1], sizes[r + 1][c])
                sizes[r + 1][c + 1] = size
                if size > best:
                    best, best_r, best_c = size, r - size + 1, c - size + 1

    grid = [list(row) for row in rows]
    for r in range(best_r, best_r + best):
        for c in range(best_c, best_c + best):
            grid[r][c] = full
    return "\n".join("".join(row) for row in grid) + "\n"


def run_with_map(text):
    """Write text to a file and run biggest_square with that file as argument"""
    with open("map.txt", "w") as f:
        f.write(text)
    return check50.run("./biggest_square map.txt")


def expect_solution(text, timeout=5):
    process = run_with_map(text)
    try:
        helpers.expect_ascii_art(process, solve(text))
    except check50.Failure as failure:
        if len(text) < 1000:
            failure.payload["help"] = f"kaart:\n{text}\n" + (failure.payload.get("help") or "")
        raise
    process.exit(0, timeout=timeout)


def expect_error(text):
    process = run_with_map(text)
    output = process.stdout().strip()
    if output != "map error":
        raise check50.Failure(
            "verwachtte alleen \"map error\" als uitvoer",
            help=f"kaart:\n{text}\njouw uitvoer:\n{output}"
        )
    check50.log("controleren of het programma stopt met exit code 1...")
    if process.exitcode != 1:
        raise check50.Failure(f"verwachtte exit code 1, niet {process.exitcode}")
