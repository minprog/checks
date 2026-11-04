import copy
import os
import sys
sys.path.append(os.path.abspath('.'))

import pytest  # noqa: E402 # ignore that this import is not top-level

from sudoku import Sudoku  # noqa: E402 # ignore that this import is not top-level
from solve import solve  # noqa: E402 # ignore that this import is not top-level


@pytest.fixture
def sudoku1():
    puzzle = [
        "7,9,0,0,0,0,3,0,1",
        "0,0,0,0,0,6,9,0,0",
        "8,0,0,0,3,0,0,7,6",
        "0,0,0,0,0,5,0,0,2",
        "0,0,5,4,1,8,7,0,0",
        "4,0,0,7,0,0,0,0,0",
        "6,1,0,0,9,0,0,0,8",
        "0,0,2,3,0,0,0,0,0",
        "0,0,9,0,0,0,0,5,4"
    ]
    puzzle = [row.replace(",", "") for row in puzzle]
    return Sudoku(puzzle)


@pytest.fixture
def sudoku1_solved():
    puzzle = [
        "7,9,6,8,5,4,3,2,1",
        "2,4,3,1,7,6,9,8,5",
        "8,5,1,2,3,9,4,7,6",
        "1,3,7,9,6,5,8,4,2",
        "9,2,5,4,1,8,7,6,3",
        "4,6,8,7,2,3,5,1,9",
        "6,1,4,5,9,7,2,3,8",
        "5,8,2,3,4,1,6,9,7",
        "3,7,9,6,8,2,1,5,4"
    ]
    puzzle = [row.replace(",", "") for row in puzzle]
    return Sudoku(puzzle)


def test_solve(sudoku1, sudoku1_solved):
    untouched = copy.deepcopy(sudoku1)
    solution = solve(sudoku1)

    for x in range(9):
        for y in range(9):
            assert solution.value_at(x, y) == sudoku1_solved.value_at(x, y)

    for x in range(9):
        for y in range(9):
            assert untouched.value_at(x, y) == 0 or solution.value_at(x, y) == untouched.value_at(x, y)
