"""
Solves a single puzzle with the sudoku module found in <implementation dir>
and prints the CPU time of that solve in seconds, or "ERROR <reason>".

Usage: python bench.py <implementation dir> <puzzle csv>

Runs in its own process so that a student's caching (e.g. lru_cache) cannot
carry over from one measurement to the next.
"""
import sys
import time


def main() -> None:
    implementationDir, puzzlePath = sys.argv[1:3]

    # solve.py lives next to this script, sudoku.py in implementationDir
    sys.path.insert(0, implementationDir)

    from sudoku import load_from_file
    from solve import solve

    # independent parse of the puzzle, to verify the givens afterwards
    with open(puzzlePath) as f:
        givens = [[int(v) for v in line.strip().split(",")] for line in f if line.strip()]

    sudoku = load_from_file(puzzlePath)

    start = time.process_time()
    solution = solve(sudoku)
    elapsed = time.process_time() - start

    if solution is None:
        print("ERROR solve() returned None, expected a solved Sudoku")
        return

    grid = [[solution.value_at(x, y) for x in range(9)] for y in range(9)]
    digits = set(range(1, 10))

    for y in range(9):
        for x in range(9):
            if givens[y][x] and givens[y][x] != grid[y][x]:
                print(f"ERROR the solution changed given value at x={x}, y={y}")
                return

    units = [row for row in grid]
    units += [[grid[y][x] for y in range(9)] for x in range(9)]
    units += [
        [grid[by + dy][bx + dx] for dy in range(3) for dx in range(3)]
        for by in (0, 3, 6) for bx in (0, 3, 6)
    ]
    if any(set(unit) != digits for unit in units):
        print("ERROR the returned Sudoku is not a valid solution")
        return

    print(f"{elapsed:.6f}")


main()
