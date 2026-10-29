import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent))

from checkpy import *
from _default_checks import checkMypy, checkStyle
from _helpers import runPythonTool


def runCinema(*inputs: str) -> str:
    exclude("*")
    include("cinema.py")
    output = outputOf(
        overwriteAttributes=[("__name__", "__main__")],
        stdinArgs=list(inputs)
    )
    return output.strip()


@passed(checkStyle, checkMypy, hide=False)
def testWeekendEveningTicketsWith3D():
    """a saturday evening 3D movie with an adult (no student card) and a child costs 25.00 in total."""
    output = runCinema("saturday", "20", "y", "2", "30", "n", "8")
    assert output == \
"""WELCOME TO THE CINEMA
Ticket 1: adult 14.50
Ticket 2: child 10.50
Total: 25.00"""


@passed(testWeekendEveningTicketsWith3D, hide=False)
def testInfantsAreFree():
    """infants get in for free: a single infant ticket results in "Total: free"."""
    output = runCinema("tuesday", "10", "n", "1", "2")
    assert output == \
"""WELCOME TO THE CINEMA
Ticket 1: infant 0.00
Total: free"""


@passed(testWeekendEveningTicketsWith3D, hide=False)
def testGroupDiscountAndStudents():
    """four tickets on a monday afternoon (student, child, senior, infant) get a 10% group discount."""
    output = runCinema("monday", "14", "n", "4", "40", "y", "10", "70", "1")
    assert output == \
"""WELCOME TO THE CINEMA
Ticket 1: student 8.50
Ticket 2: child 6.00
Ticket 3: senior 7.50
Ticket 4: infant 0.00
Group discount: -2.20
Total: 19.80"""


@passed(testWeekendEveningTicketsWith3D, hide=False)
def testInvalidInputIsReprompted():
    """a friday morning 3D movie works, and invalid input is asked again."""
    output = runCinema(
        "x", "Friday", "25", "9", "3d", "y", "0", "11", "2",
        "121", "5", "64", "q", "y"
    )
    assert output == \
"""WELCOME TO THE CINEMA
Ticket 1: child 7.00
Ticket 2: student 9.50
Total: 16.50"""


@passed(testWeekendEveningTicketsWith3D, hide=False)
def testSundayGroup():
    """five tickets on a sunday night get a group discount and the correct surcharges."""
    output = runCinema("Sunday", "23", "n", "5", "1", "2", "3", "64", "n", "65", "y", "0")
    assert output == \
"""WELCOME TO THE CINEMA
Ticket 1: infant 0.00
Ticket 2: infant 0.00
Ticket 3: child 8.50
Ticket 4: adult 12.50
Ticket 5: senior 10.00
Group discount: -3.10
Total: 27.90"""


@passed(
    testInfantsAreFree, testGroupDiscountAndStudents,
    testInvalidInputIsReprompted, testSundayGroup, hide=False
)
def testCyclomaticComplexity():
    """flake8 --max-complexity=3 --select=C cinema.py shows no violations"""
    result = runPythonTool("flake8", ["--max-complexity=3", "--select=C", file])
    assert "C901" not in result.stdout
