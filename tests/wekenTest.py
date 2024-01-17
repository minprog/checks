from checkpy import *
from _default_checks import *
from _helpers import testPytestFail
checkPytest.nTests = 4

exclude("*")
require(file.name, f"test_{file.name}")

@passed(*allDefaults, hide=False)
def testTests():
    """pytest tests falen bij verschillende incorrecte implementaties"""
    def weeks_elapsed(day1: int, day2: int) -> int:
        return 7
    testPytestFail(weeks_elapsed)

    def weeks_elapsed(day1: int, day2: int) -> int:
        return (day1 - day2) // 7
    testPytestFail(weeks_elapsed)

@passed(testTests, hide=False)
def testFunction():
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

@passed(testFunction, hide=False)
def testProgram():
    """het programma weken.py werkt correct met invoer en uitvoer"""
    output = outputOf(stdinArgs=[3, 20], overwriteAttributes=[("__name__", "__main__")])
    assert output == "Er zijn 2 volle weken verstreken.\n"
