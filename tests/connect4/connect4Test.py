import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent))

from checkpy import *
from _default_checks import checkMypy, checkStyle
from _helpers import runPythonTool

EXPECTED_DIR = pathlib.Path(__file__).parent / "expected"


def playGame(name: str, inputs: str) -> None:
    """Play connect4.py with comma separated inputs, compare to expected/<name>.txt."""
    exclude("*")
    include("connect4.py", "board.py")

    output = outputOf(
        overwriteAttributes=[("__name__", "__main__")],
        stdinArgs=inputs.split(",")
    )

    expected = (EXPECTED_DIR / f"{name}.txt").read_text().strip()
    assert output.strip() == expected


@passed(checkStyle, checkMypy, hide=False)
def testHorizontalWin():
    """X wins horizontally (columns 1, 1, 2, 2, 3, 3, 4) and the players do not play again."""
    playGame("testHorizontalWin", "1,1,2,2,3,3,4,n")


@passed(testHorizontalWin, hide=False)
def testVerticalWinAndInvalidColumns():
    """invalid columns (x, 0, 8) are asked again and O wins vertically."""
    playGame("testVerticalWinAndInvalidColumns", "x,0,8,1,2,3,2,3,2,4,2,n")


@passed(testHorizontalWin, hide=False)
def testFullColumn():
    """choosing a full column is not allowed and the player is asked again."""
    playGame("testFullColumn", "1,1,1,1,1,1,1,2,3,2,3,2,3,2,n")


@passed(testHorizontalWin, hide=False)
def testDiagonalWinsAndScore():
    """two games, each ending in a diagonal win, the score is kept between games."""
    playGame(
        "testDiagonalWinsAndScore",
        "2,2,1,4,4,6,4,4,1,5,6,2,7,6,3,3,1,3,3,1,y,"
        "3,5,5,2,1,3,2,4,3,6,6,6,5,5,2,5,1,1,4,3,6,n"
    )


@passed(testHorizontalWin, hide=False)
def testDraw():
    """a full board without four in a row ends in a draw."""
    playGame(
        "testDraw",
        "4,4,2,7,6,1,2,2,5,3,7,7,2,5,2,3,4,2,5,4,5,5,6,3,4,7,4,1,7,5,3,7,1,6,6,6,6,3,1,3,1,1,n"
    )


@passed(testHorizontalWin, hide=False)
def testPlayAgainInvalid():
    """an invalid answer to "Play again?" is asked again, y starts a new game."""
    playGame("testPlayAgainInvalid", "1,1,2,2,3,3,4,maybe,Y,y,1,1,2,2,3,3,4,n")


@passed(
    testVerticalWinAndInvalidColumns, testFullColumn,
    testDiagonalWinsAndScore, testDraw, testPlayAgainInvalid, hide=False
)
def testCyclomaticComplexity():
    """flake8 --max-complexity=3 --select=C connect4.py board.py shows no violations"""
    result = runPythonTool(
        "flake8", ["--max-complexity=3", "--select=C", "connect4.py", "board.py"]
    )
    assert "C901" not in result.stdout
