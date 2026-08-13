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


# The scene as pinned by the assignment: 80 wide, 40 deep
HEIGHT = 40
WIDTH = 80

# Any of the ANSI sequences that clear the screen marks the end of a frame
CLEAR = r"\x1b\[[0-3]?J|\x1bc"

# The tests below print the scene themselves, as one "row,column" per line,
# so that a broken draw_scene cannot make the other checks fail too
DUMP_SCENE = r"""
void dump_scene(bool scene[40][80])
{
    for (int row = 0; row < 40; row++)
    {
        for (int column = 0; column < 80; column++)
        {
            if (scene[row][column])
            {
                printf("%i,%i\n", row, column);
            }
        }
    }
    printf("END\n");
}
"""


def compile_with(main):
    """Replace the student's main with ours, then compile"""
    return helpers.replace_main("snowfall.c", DUMP_SCENE + main)


def flakes(output):
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
    """Run the compiled program and return the scene it printed"""
    return flakes(check50.run("./snowfall").stdout(timeout=10))


def describe(coordinates):
    """Describe a scene the way the student can recognise it"""
    if not coordinates:
        return "an empty scene"
    return ", ".join(f"({row},{column})" for row, column in sorted(coordinates))


def strip_ansi(text):
    """Remove colour codes and other escape sequences"""
    text = re.sub(r"\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)", "", text)
    return re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]|\x1b[c()][0-9A-B]?", "", text)


@check50.check()
def exists():
    "snowfall.c exists"
    check50.exists("snowfall.c")


def declare_xopen_source():
    """drand48 and friends are only declared when _XOPEN_SOURCE is defined"""
    with open("snowfall.c") as f:
        content = f.read()

    if "_XOPEN_SOURCE" not in content and ("drand48" in content or "srand48" in content):
        with open("snowfall.c", "w") as f:
            f.write("#define _XOPEN_SOURCE 500\n" + content)


@check50.check(exists)
def compiles():
    "snowfall.c compiles"
    declare_xopen_source()

    main = r"""
int main(void)
{
}
"""
    with helpers.replace_main("snowfall.c", main):
        check50.c.compile("snowfall.c", lcs50=True)


@check50.check(compiles)
def has_functions():
    "snowfall.c has the functions: add_flake, fall, and draw_scene"
    with open("snowfall.c") as f:
        content = f.read()

    for name in ["add_flake", "fall", "draw_scene"]:
        if f" {name}(" not in content and f" {name} (" not in content:
            raise check50.Failure(
                f"Missing function: {name}",
                help="the assignment asks for the functions add_flake, fall and "
                     "draw_scene; you are free to add any other functions you like"
            )


@check50.check(has_functions)
def fall_moves_snow_down():
    "fall() moves a snowflake one row down"
    main = r"""
int main(void)
{
    bool scene[40][80] = {false};
    scene[0][5] = true;
    fall(scene);
    dump_scene(scene);
}
"""
    with compile_with(main):
        check50.c.compile("snowfall.c", lcs50=True)

        found = run_dump()

        if len(found) != 1:
            raise check50.Failure(
                f"after one timestep the scene held {len(found)} snowflakes "
                f"instead of 1: {describe(found)}",
                help="fall() should move each snowflake, not add or remove any"
            )

        row, column = found[0]

        if row != 1:
            raise check50.Failure(
                f"a snowflake at row 0 ended up at row {row} instead of row 1",
                help="every timestep, a snowflake that can fall moves down exactly "
                     "one row"
            )

        # A little sideways drift is fine, in case of a wind effect
        if abs(column - 5) > 2:
            raise check50.Failure(
                f"a snowflake in column 5 ended up in column {column}"
            )


@check50.check(has_functions)
def fall_keeps_snow_at_the_bottom():
    "fall() leaves a snowflake on the bottom row where it is"
    main = r"""
int main(void)
{
    bool scene[40][80] = {false};
    scene[39][5] = true;
    fall(scene);
    fall(scene);
    dump_scene(scene);
}
"""
    with compile_with(main):
        check50.c.compile("snowfall.c", lcs50=True)

        found = run_dump()

        if len(found) != 1:
            raise check50.Failure(
                f"a snowflake on the bottom row disappeared: the scene now holds "
                f"{describe(found)}",
                help="when a snowflake reaches the bottom of the screen, it stays there"
            )

        row, _ = found[0]

        if row != 39:
            raise check50.Failure(
                f"a snowflake on the bottom row (39) moved to row {row}",
                help="when a snowflake reaches the bottom of the screen, it stays there"
            )


@check50.check(has_functions)
def fall_stacks_snow():
    "fall() leaves a snowflake resting on other snow where it is"
    main = r"""
int main(void)
{
    bool scene[40][80] = {false};
    scene[39][5] = true;
    scene[38][5] = true;
    fall(scene);
    dump_scene(scene);
}
"""
    with compile_with(main):
        check50.c.compile("snowfall.c", lcs50=True)

        found = run_dump()

        if sorted(found) != [(38, 5), (39, 5)]:
            raise check50.Failure(
                f"two stacked snowflakes at (38,5) and (39,5) became "
                f"{describe(found)}",
                help="when a snowflake is on top of another snowflake, it stays there"
            )


@check50.check(has_functions)
def fall_does_not_smear():
    "fall() moves a column of snowflakes down without losing any"
    main = r"""
int main(void)
{
    bool scene[40][80] = {false};
    scene[0][5] = true;
    scene[1][5] = true;
    scene[2][5] = true;
    scene[3][5] = true;
    fall(scene);
    dump_scene(scene);
}
"""
    with compile_with(main):
        check50.c.compile("snowfall.c", lcs50=True)

        found = run_dump()

        if len(found) != 4:
            raise check50.Failure(
                f"four snowflakes above each other became {len(found)} after one "
                f"timestep: {describe(found)}",
                help="while looping over the scene you are also changing it, so a "
                     "snowflake can be moved more than once in one timestep"
            )

        rows = sorted(row for row, _ in found)

        if rows != [1, 2, 3, 4]:
            raise check50.Failure(
                f"four snowflakes in rows 0, 1, 2, 3 ended up in rows "
                f"{', '.join(str(row) for row in rows)} instead of 1, 2, 3, 4"
            )


@check50.check(has_functions)
def add_flake_adds_snow_at_the_top():
    "add_flake() adds a snowflake at the top of the scene"
    main = r"""
int main(void)
{
    bool scene[40][80] = {false};
    add_flake(scene);
    dump_scene(scene);
}
"""
    with compile_with(main):
        check50.c.compile("snowfall.c", lcs50=True)

        found = run_dump()

        if not found:
            raise check50.Failure(
                "add_flake() did not add a snowflake to an empty scene",
                help="add_flake() should add new snow in the top row of the scene"
            )

        # Adding a few flakes at once is fine, they just have to be at the top
        too_low = [(row, column) for row, column in found if row > 1]

        if too_low:
            raise check50.Failure(
                f"add_flake() added snow below the top of the scene: "
                f"{describe(too_low)}",
                help="new snowflakes appear at the top of the scene, in row 0"
            )


@check50.check(has_functions)
def add_flake_is_random():
    "add_flake() adds snow at random columns"
    main = r"""
int main(void)
{
    for (int i = 0; i < 200; i++)
    {
        bool scene[40][80] = {false};
        add_flake(scene);
        dump_scene(scene);
    }
}
"""
    with compile_with(main):
        check50.c.compile("snowfall.c", lcs50=True)

        output = check50.run("./snowfall").stdout(timeout=10)
        columns = [column for _, column in flakes(output.replace("END", ""))]

        if len(columns) < 5:
            raise check50.Failure(
                f"add_flake() added snow only {len(columns)} times in 200 calls",
                help="add_flake() should add a snowflake every time it is called"
            )

        distinct = len(set(columns))

        if distinct < 8:
            raise check50.Failure(
                f"200 calls to add_flake() used only {distinct} different columns",
                help="new snowflakes should appear at random positions at the top"
            )


@check50.check(has_functions)
def draw_scene_prints_the_scene():
    "draw_scene() prints the scene, using * for a snowflake"
    main = r"""
int main(void)
{
    bool scene[40][80] = {false};
    scene[0][0] = true;
    scene[3][10] = true;
    scene[39][79] = true;
    draw_scene(scene);
}
"""
    with compile_with(main):
        check50.c.compile("snowfall.c", lcs50=True)

        output = strip_ansi(check50.run("./snowfall").stdout(timeout=10))
        lines = output.replace("\r\n", "\n").split("\n")

        if len(lines) < HEIGHT:
            raise check50.Failure(
                f"draw_scene() printed {len(lines)} lines, expected at least {HEIGHT}",
                help=f"the scene is {HEIGHT} rows deep, so drawing it takes "
                     f"{HEIGHT} lines"
            )

        # Allow a title or border above the scene: look for the row that holds
        # the flake we put in the top-left corner
        offsets = [i for i, line in enumerate(lines[:len(lines) - HEIGHT + 1])
                   if line.startswith("*")]

        if not offsets:
            raise check50.Failure(
                "could not find the snowflake at row 0, column 0 in the output of "
                "draw_scene()",
                help="draw a snowflake as a * and an empty spot as a space"
            )

        offset = offsets[0]

        for row, column in [(3, 10), (39, 79)]:
            line = lines[offset + row]

            if len(line) <= column or line[column] != "*":
                raise check50.Failure(
                    f"expected a * at row {row}, column {column} of the scene, "
                    f"but found {'nothing' if len(line) <= column else repr(line[column])}",
                    help="every snowflake in the scene is drawn as a * at its own "
                         "row and column"
                )


# Note: this check depends on exists, not on compiles, because the checks above
# leave their own main behind in snowfall.c. Here we need the student's own main.
@check50.check(exists, timeout=90)
def animates():
    "snowfall runs an animation, clearing the screen every timestep"
    declare_xopen_source()

    # Speed up the animation, so the check does not have to wait for it
    with open("snowfall.c") as f:
        content = f.read()

    includes = list(re.finditer(r"^\s*#\s*include\s*[<\"][^>\"]+[>\"]", content,
                                re.MULTILINE))
    speedup = ("\n#include <unistd.h>\n"
               "#define usleep(x) (0)\n"
               "#define sleep(x) (0)\n"
               "#define nanosleep(a, b) (0)\n")
    position = includes[-1].end() if includes else 0

    with open("snowfall.c", "w") as f:
        f.write(content[:position] + speedup + content[position:])

    try:
        check50.c.compile("snowfall.c", lcs50=True)
    finally:
        with open("snowfall.c", "w") as f:
            f.write(content)

    process = check50.run("./snowfall")
    frames = 0
    finished = False

    try:
        for _ in range(12):
            process.process.expect(CLEAR, timeout=5)
            frames += 1
    except pexpect.TIMEOUT:
        pass
    except pexpect.EOF:
        finished = True
    finally:
        signalstatus = process.process.signalstatus
        process.kill()

    if frames < 8:
        if signalstatus is not None:
            raise check50.Failure(
                f"the program crashed after {frames} timesteps"
            )

        raise check50.Failure(
            f"saw only {frames} timesteps of the animation"
            + (", after which the program stopped" if finished else ""),
            help="every timestep the program should clear the screen by printing "
                 "\\033[2J and then draw the scene. Note that this check switches "
                 "off usleep(), sleep() and nanosleep() to speed up the animation; "
                 "a timing loop that keeps busy instead of sleeping cannot be sped "
                 "up and will time out here."
        )
