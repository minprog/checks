import re

import pexpect

import check50
import check50.c
import check50.internal

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)
helpers.set_stdout_limit(2000)


# The world as pinned by the assignment: 80 wide, 40 deep
HEIGHT = 40
WIDTH = 80

# Any of the ANSI sequences that clear the screen marks the end of a frame
CLEAR = r"\x1b\[[0-3]?J|\x1bc"

# The tests below print the world themselves, as one "row,column" per line, so
# that a broken draw_world cannot make the other checks fail too
DUMP_WORLD = r"""
void dump_world(bool world[40][80])
{
    for (int row = 0; row < 40; row++)
    {
        for (int column = 0; column < 80; column++)
        {
            if (world[row][column])
            {
                printf("%i,%i\n", row, column);
            }
        }
    }
    printf("END\n");
}
"""

# What you get from a blinker when you overwrite the world while reading it,
# for the usual ways of looping over a 2-dimensional array
IN_PLACE = {
    ((19, 41), (19, 42), (20, 40), (20, 42)): "row by row, from top to bottom",
    ((19, 40), (19, 41), (20, 40), (20, 42)): "row by row, from right to left",
    ((20, 40), (20, 42), (21, 41), (21, 42)): "row by row, from bottom to top",
    (): "column by column",
}


def compile_with(main):
    """Replace the student's main with ours, then compile"""
    return helpers.replace_main("game_of_life.c", DUMP_WORLD + main)


def live_cells(output):
    """Collect the (row, column) pairs that the injected main printed"""
    coordinates = []

    for line in output.replace("\r\n", "\n").split("\n"):
        line = line.strip()

        if line == "END":
            break

        match = re.fullmatch(r"(\d+),(\d+)", line)
        if match:
            coordinates.append((int(match.group(1)), int(match.group(2))))

    return coordinates


def run_dump():
    """Run the compiled program and return the world it printed"""
    return live_cells(check50.run("./game_of_life").stdout(timeout=10))


def describe(coordinates):
    """Describe a world the way the student can recognise it"""
    if not coordinates:
        return "an empty world"
    return ", ".join(f"({row},{column})" for row, column in sorted(coordinates))


def expect_cells(found, expected, rationale, help=None):
    """Compare a world against the expected one, naming what went wrong"""
    found = sorted(found)
    expected = sorted(expected)

    if found == expected:
        return

    missing = [cell for cell in expected if cell not in found]
    extra = [cell for cell in found if cell not in expected]

    details = []
    if missing:
        details.append(f"these cells should have been alive: {describe(missing)}")
    if extra:
        details.append(f"these cells should have been dead: {describe(extra)}")

    raise check50.Failure(f"{rationale}; {' and '.join(details)}", help=help)


def strip_ansi(text):
    """Remove colour codes and other escape sequences"""
    text = re.sub(r"\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)", "", text)
    return re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]|\x1b[c()][0-9A-B]?", "", text)


@check50.check()
def exists():
    "game_of_life.c exists"
    check50.exists("game_of_life.c")


@check50.check(exists)
def compiles():
    "game_of_life.c compiles"
    main = r"""
int main(void)
{
}
"""
    with helpers.replace_main("game_of_life.c", main):
        check50.c.compile("game_of_life.c", lcs50=True)


@check50.check(compiles)
def has_functions():
    "game_of_life.c has the functions: next_generation and draw_world"
    with open("game_of_life.c") as f:
        content = f.read()

    for name in ["next_generation", "draw_world"]:
        if f" {name}(" not in content and f" {name} (" not in content:
            raise check50.Failure(
                f"Missing function: {name}",
                help="the assignment asks for the functions next_generation and "
                     "draw_world; you are free to add any other functions you like"
            )


@check50.check(has_functions)
def block_stays_the_same():
    "next_generation() leaves a block of four cells alone"
    main = r"""
int main(void)
{
    bool world[40][80] = {false};
    world[20][40] = true;
    world[20][41] = true;
    world[21][40] = true;
    world[21][41] = true;
    next_generation(world);
    next_generation(world);
    dump_world(world);
}
"""
    with compile_with(main):
        check50.c.compile("game_of_life.c", lcs50=True)

        expect_cells(
            run_dump(),
            [(20, 40), (20, 41), (21, 40), (21, 41)],
            "a block of four cells should stay exactly the same",
            help="every cell of a block has three living neighbours, so all four "
                 "stay alive. The cells around it have at most two living "
                 "neighbours, so none of them come to life"
        )


@check50.check(has_functions)
def lonely_cells_die():
    "next_generation() kills cells with fewer than two neighbours"
    main = r"""
int main(void)
{
    bool world[40][80] = {false};
    world[20][40] = true;
    next_generation(world);
    dump_world(world);

    bool pair[40][80] = {false};
    pair[20][40] = true;
    pair[20][41] = true;
    next_generation(pair);
    dump_world(pair);
}
"""
    with compile_with(main):
        check50.c.compile("game_of_life.c", lcs50=True)

        output = check50.run("./game_of_life").stdout(timeout=10)
        worlds = output.replace("\r\n", "\n").split("END")

        expect_cells(
            live_cells(worlds[0]), [],
            "a single living cell has no neighbours at all, so it should die",
            help="a living cell with fewer than two living neighbours dies"
        )
        expect_cells(
            live_cells(worlds[1]), [],
            "two living cells next to each other each have only one neighbour, "
            "so both should die",
            help="a living cell with fewer than two living neighbours dies"
        )


@check50.check(has_functions)
def crowded_cells_die():
    "next_generation() kills a cell with four neighbours"
    main = r"""
int main(void)
{
    bool world[40][80] = {false};
    world[19][40] = true;
    world[20][39] = true;
    world[20][40] = true;
    world[20][41] = true;
    world[21][40] = true;
    next_generation(world);
    dump_world(world);
}
"""
    with compile_with(main):
        check50.c.compile("game_of_life.c", lcs50=True)

        expect_cells(
            run_dump(),
            [(19, 39), (19, 40), (19, 41),
             (20, 39), (20, 41),
             (21, 39), (21, 40), (21, 41)],
            "the middle cell of a plus shape has four living neighbours, so it "
            "should die, while the four corners around it come to life",
            help="a living cell with more than three living neighbours dies"
        )


@check50.check(has_functions)
def dead_cells_come_to_life():
    "next_generation() brings a dead cell with three neighbours to life"
    main = r"""
int main(void)
{
    bool world[40][80] = {false};
    world[20][40] = true;
    world[20][41] = true;
    world[21][40] = true;
    next_generation(world);
    dump_world(world);
}
"""
    with compile_with(main):
        check50.c.compile("game_of_life.c", lcs50=True)

        expect_cells(
            run_dump(),
            [(20, 40), (20, 41), (21, 40), (21, 41)],
            "three cells in an L shape should become a block of four",
            help="the empty spot at (21,41) has exactly three living neighbours, "
                 "so a new cell is born there"
        )


@check50.check(has_functions)
def blinker_oscillates():
    "next_generation() flips a blinker, and flips it back"
    main = r"""
int main(void)
{
    bool world[40][80] = {false};
    world[20][40] = true;
    world[20][41] = true;
    world[20][42] = true;
    next_generation(world);
    dump_world(world);
    next_generation(world);
    dump_world(world);
}
"""
    with compile_with(main):
        check50.c.compile("game_of_life.c", lcs50=True)

        output = check50.run("./game_of_life").stdout(timeout=10)
        worlds = output.replace("\r\n", "\n").split("END")

        expect_cells(
            live_cells(worlds[0]),
            [(19, 41), (20, 41), (21, 41)],
            "a horizontal blinker should become a vertical one",
            help="the two outer cells have only one neighbour and die, while the "
                 "cells above and below the middle have three neighbours and are born"
        )
        expect_cells(
            live_cells(worlds[1]),
            [(20, 40), (20, 41), (20, 42)],
            "after two generations a blinker should be back where it started"
        )


@check50.check(has_functions)
def next_generation_is_simultaneous():
    "next_generation() updates every cell from the same old generation"
    main = r"""
int main(void)
{
    bool world[40][80] = {false};
    world[20][40] = true;
    world[20][41] = true;
    world[20][42] = true;
    next_generation(world);
    dump_world(world);
}
"""
    with compile_with(main):
        check50.c.compile("game_of_life.c", lcs50=True)

        found = sorted(run_dump())
        expected = [(19, 41), (20, 41), (21, 41)]

        if found == expected:
            return

        help = ("all cells change at the same moment, based on the old "
                "generation. Count the neighbours of every cell first, and only "
                "then change the world; otherwise cells you already updated "
                "influence the cells you look at next. The assignment Satellite "
                "explains this pitfall under \"Let op met in-place aanpassingen\"")

        # Point at the bug directly when the result is one we recognise
        order = IN_PLACE.get(tuple(found))
        if order is not None:
            raise check50.Failure(
                f"a blinker became {describe(found)}, which is exactly what you "
                f"get when you change the world while looping over it "
                f"{order}",
                help=help
            )

        expect_cells(found, expected,
                     "a blinker should become a vertical line of three cells",
                     help=help)


@check50.check(has_functions)
def glider_moves():
    "a glider moves one cell diagonally in four generations"
    main = r"""
int main(void)
{
    bool world[40][80] = {false};
    world[10][20] = true;
    world[11][21] = true;
    world[12][19] = true;
    world[12][20] = true;
    world[12][21] = true;
    for (int i = 0; i < 4; i++)
    {
        next_generation(world);
    }
    dump_world(world);
}
"""
    with compile_with(main):
        check50.c.compile("game_of_life.c", lcs50=True)

        expect_cells(
            run_dump(),
            [(11, 21), (12, 22), (13, 20), (13, 21), (13, 22)],
            "after four generations a glider should be back in its own shape, "
            "one row down and one column to the right",
            help="a glider keeps its five cells in every generation. If it falls "
                 "apart, check that you look at all eight neighbours of a cell"
        )


@check50.check(has_functions)
def draw_world_prints_the_world():
    "draw_world() prints the world, using # for a living cell"
    cells = [(0, 0), (0, 79), (1, 3), (2, 1), (5, 10), (19, 40), (39, 0), (39, 79)]

    main = r"""
int main(void)
{
    bool world[40][80] = {false};
""" + "".join(f"    world[{row}][{column}] = true;\n" for row, column in cells) + r"""
    draw_world(world);
}
"""
    with compile_with(main):
        check50.c.compile("game_of_life.c", lcs50=True)

        output = strip_ansi(check50.run("./game_of_life").stdout(timeout=10))
        lines = output.replace("\r\n", "\n").split("\n")

        if len(lines) < HEIGHT:
            raise check50.Failure(
                f"draw_world() printed {len(lines)} lines, expected at least {HEIGHT}",
                help=f"the world is {HEIGHT} rows deep, so drawing it takes "
                     f"{HEIGHT} lines"
            )

        alive = set(cells)

        def mismatches(row_offset, column_offset):
            """Cells that do not match, for one alignment of the world"""
            wrong = []
            for row in range(HEIGHT):
                line = lines[row_offset + row]
                for column in range(WIDTH):
                    index = column_offset + column
                    character = line[index] if index < len(line) else " "
                    if ((row, column) in alive) != (character == "#"):
                        wrong.append((row, column, character))
            return wrong

        # Allow a title above the world and a border to the left of it
        alignments = [(row_offset, column_offset)
                      for row_offset in range(len(lines) - HEIGHT + 1)
                      for column_offset in range(5)]

        best = min((mismatches(*alignment) for alignment in alignments), key=len)

        if best:
            row, column, character = best[0]
            expected = "#" if (row, column) in alive else "a space"
            raise check50.Failure(
                f"expected {expected} at row {row}, column {column} of the world, "
                f"but found {character!r} ({len(best)} cells are wrong)",
                help="draw a living cell as a # and a dead cell as a space, one "
                     "line per row of the world"
            )


# Note: this check depends on exists, not on compiles, because the checks above
# leave their own main behind in game_of_life.c. Here we need the student's own.
@check50.check(exists, timeout=120)
def animates():
    "game_of_life runs an animation of an interesting world"

    # Speed up the animation, so the check does not have to wait for it
    with open("game_of_life.c") as f:
        content = f.read()

    includes = list(re.finditer(r"^\s*#\s*include\s*[<\"][^>\"]+[>\"]", content,
                                re.MULTILINE))
    speedup = ("\n#include <unistd.h>\n"
               "#define usleep(x) (0)\n"
               "#define sleep(x) (0)\n"
               "#define nanosleep(a, b) (0)\n")
    position = includes[-1].end() if includes else 0

    with open("game_of_life.c", "w") as f:
        f.write(content[:position] + speedup + content[position:])

    try:
        check50.c.compile("game_of_life.c", lcs50=True)
    finally:
        with open("game_of_life.c", "w") as f:
            f.write(content)

    process = check50.run("./game_of_life")
    frames = []
    finished = False

    try:
        for _ in range(20):
            process.process.expect(CLEAR, timeout=5)
            frames.append(strip_ansi(process.process.before))
    except pexpect.TIMEOUT:
        pass
    except pexpect.EOF:
        finished = True
    finally:
        signalstatus = process.process.signalstatus
        process.kill()

    if len(frames) < 8:
        if signalstatus is not None:
            raise check50.Failure(
                f"the program crashed after {len(frames)} generations"
            )

        raise check50.Failure(
            f"saw only {len(frames)} generations of the animation"
            + (", after which the program stopped" if finished else ""),
            help="every generation the program should clear the screen by printing "
                 "\\033[2J and then draw the world, and it should keep going until "
                 "the user stops it. Note that this check switches off usleep(), "
                 "sleep() and nanosleep() to speed up the animation; a timing loop "
                 "that keeps busy instead of sleeping cannot be sped up and will "
                 "time out here."
        )

    # Skip anything before the world is first drawn, so a splash screen or a
    # program that clears the screen after drawing is fine
    drawn = [frame for frame in frames if "#" in frame]

    if not drawn or drawn[0].count("#") < 3:
        raise check50.Failure(
            "the world is empty when the animation starts"
            if not drawn else
            f"the world holds only {drawn[0].count('#')} living cells when the "
            f"animation starts",
            help="start from an interesting configuration: put a few living cells "
                 "in the world before the animation begins"
        )

    if all(frame == drawn[0] for frame in drawn):
        raise check50.Failure(
            "the world looks exactly the same in every generation",
            help="start from a configuration that actually changes. A block or "
                 "another still life never changes, so it does not make for an "
                 "interesting animation. Also check that main() calls "
                 "next_generation()"
        )
