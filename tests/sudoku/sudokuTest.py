import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from checkpy import *
from _default_checks import *

import subprocess
import sys

# Seconds of CPU time the original (distribution) sudoku.py needs per puzzle,
# measured on a reference machine with `python bench.py baseline puzzles/N.csv`.
# Ordered from cheapest to most expensive.
REFERENCE_SECONDS = {2: 0.25, 3: 2.24, 6: 10.90, 1: 13.41, 5: 36.22, 4: 60.61}

# The puzzles used to find out how fast this machine is compared to the
# reference machine, by running the original sudoku.py on them.
CALIBRATION_PUZZLES = (2, 3)

# Measure each puzzle up to this many times (fresh process each time), keep the
# fastest. Repeating is skipped for puzzles that already take a while.
MAX_REPEATS = 3
REPEAT_BELOW_SECONDS = 1.0

# Stop early (and don't waste server time) when the solution is clearly not
# faster than the original after at least this many puzzles.
EARLY_STOP_AFTER = 3
EARLY_STOP_BELOW_SPEEDUP = 1.2

# the original test cases from the distribution code (test_sudoku.py, test_solve.py)
checkPytest.nTests = 13

# test_solve.py solves a puzzle, which takes ~15 seconds with the original code
checkPytest.timeout = 120

exclude("*")
require(file.name)
includeFromTests("solve.py", "bench.py", "puzzles/*.csv", "baseline/sudoku.py", "pytest_tests/*.py")


class BenchError(AssertionError):
    pass


def bench(implementationDir: str, puzzle: int, timeout: float) -> float:
    """CPU seconds needed to solve puzzle, via bench.py in a fresh process."""
    try:
        result = subprocess.run(
            [sys.executable, "bench.py", implementationDir, f"puzzles/{puzzle}.csv"],
            capture_output=True,
            universal_newlines=True,
            timeout=timeout
        )
    except subprocess.TimeoutExpired:
        raise BenchError(
            f"solving puzzle {puzzle} took more than {timeout:.0f} seconds, "
            "which is far slower than the original code"
        )

    out = result.stdout.strip().splitlines()
    if result.returncode != 0 or not out:
        lastLine = result.stderr.strip().splitlines()[-1:] or ["unknown error"]
        raise BenchError(f"running puzzle {puzzle} crashed: {lastLine[0]}")

    if out[-1].startswith("ERROR"):
        raise BenchError(f"puzzle {puzzle}: {out[-1][len('ERROR '):]}")

    return float(out[-1])


def significant(value: float) -> str:
    """Format with two significant digits, e.g. 38.4 -> '38', 1.234 -> '1.2'."""
    return f"{float(f'{value:.2g}'):g}"


def formatSeconds(seconds: float) -> str:
    return f"{seconds:.2f} s" if seconds >= 1 else f"{seconds * 1000:.1f} ms"


@passed(*allDefaults, hide=False, timeout=600)
def testSpeedup(test):
    """estimates how much faster your sudoku.py is than the original"""
    # How fast is this machine compared to the reference machine?
    measured = sum(bench("baseline", p, timeout=60) for p in CALIBRATION_PUZZLES)
    scale = measured / sum(REFERENCE_SECONDS[p] for p in CALIBRATION_PUZZLES)

    originalTotal = 0.0
    studentTotal = 0.0
    lines = []
    stoppedEarly = False

    for done, (puzzle, reference) in enumerate(REFERENCE_SECONDS.items(), start=1):
        original = reference * scale

        # a hopelessly slow solution is cut off after a few times the original
        timeout = max(10.0, 3 * original)

        times = [bench(".", puzzle, timeout)]
        while len(times) < MAX_REPEATS and times[-1] < REPEAT_BELOW_SECONDS:
            times.append(bench(".", puzzle, timeout))
        student = min(times)

        originalTotal += original
        studentTotal += student
        lines.append(
            f"puzzle {puzzle}: {formatSeconds(original):>8} -> {formatSeconds(student):>8}  "
            f"({significant(original / max(student, 1e-6))}x faster)"
        )

        if done >= EARLY_STOP_AFTER and originalTotal / studentTotal < EARLY_STOP_BELOW_SPEEDUP:
            stoppedEarly = len(REFERENCE_SECONDS) > done
            break

    speedup = originalTotal / max(studentTotal, 1e-6)

    summary = [
        "estimated time of the original -> your time",
        *lines,
    ]
    if stoppedEarly:
        summary += ["", "Not all puzzles were timed: there is no meaningful speedup yet."]
    summary += [
        "",
        "This is an estimate: timings are relative to the original code run on the",
        "same machine, but still fluctuate a bit between submissions.",
    ]

    test.description = f"your sudoku.py is approximately {significant(speedup)}x as fast as the original"
    test.success = lambda info: "\n".join(summary)
