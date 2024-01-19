from checkpy import *
from _default_checks import *
from _helpers import testPytestFail
checkPytest.nTests = 4

exclude("*")
require(file.name, f"test_{file.name}")

@passed(*allDefaults, hide=False)
def testTests():
    """pytest tests falen bij verschillende incorrecte implementaties"""
    def title(string: str) -> str:
        return ""
    testPytestFail(title)

    def title(string: str) -> str:
        return string.title()[:-1]
    testPytestFail(title)

    def title(string: str) -> str:
        return string.capitalize()
    testPytestFail(title)

@passed(testTests, hide=False)
def testFunction():
    """title werkt correct"""
    calls = static.getFunctionCalls()
    for call in calls:
        if call.endswith((".title")):
            raise AssertionError(
                "don't use python's built-in title method in this assignment"
            )

    (declarative.function("title")
        .params("string")
        .returnType(str)
        .call("hello, world!")
        .returns("hello, world!".title())
        .call("")
        .returns("".title())
        .call("a,b,c,D,E,F")
        .returns("a,b,c,D,E,F".title())
        .call("MOST_DEFINITELY")
        .returns("MOST_DEFINITELY".title())
    )()