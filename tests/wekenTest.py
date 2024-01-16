from checkpy import *
from _default_checks import *
checkPytest.nTests = 4

exclude("*")
require("weken.py", "test_weken.py")

@passed(*allDefaults, hide=False)
def testWeeksElapsed():
    """weeks_elapsed werkt correct"""
    (declarative.function("weeks_elapsed")
        .params("day1", "day2")
        .returnType(int)
        .call(3, 20)
        .returns(2)
        .call(20, 3)
        .returns(2)
        .call(1, 1)
        .returns(0)
    )()

@passed(*allDefaults, hide=False)
def testProgram():
    """het programma weken.py werkt correct met invoer en uitvoer"""
    output = outputOf(stdinArgs=[3, 20], overwriteAttributes=[("__name__", "__main__")])
    assert output == "Er zijn 2 volle weken verstreken.\n"
