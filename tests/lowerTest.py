from checkpy import *
from _default_checks import *
from _helpers import testPytestFail
checkPytest.nTests = 6

exclude("*")
require(file.name, f"test_{file.name}")

@passed(*allDefaults, hide=False)
def testTests():
    """pytest tests falen bij verschillende incorrecte implementaties"""
    # lower tests
    def lower(string: str) -> str:
        return "abc"
    def upper(string: str) -> str:
        return string.upper()
    testPytestFail(lower, upper)

    def lower(string: str) -> str:
        return string
    testPytestFail(lower, upper)

    # upper tests
    def lower(string: str) -> str:
        return string.lower()
    def upper(string: str) -> str:
        return "ABC"
    testPytestFail(lower, upper)

    def upper(string: str) -> str:
        return string
    testPytestFail(lower, upper)


@passed(testTests, hide=False)
def testFunction():
    """lower en upper werken correct"""
    calls = static.getFunctionCalls()
    for call in calls:
        if call.endswith((".lower", ".upper")):
            raise AssertionError(
                "don't use python's built-in lower/upper methods in this assignment"
            )

    (declarative.function("lower")
        .params("string")
        .returnType(str)
        .call("abc")
        .returns("abc")
        .call("DEF")
        .returns("def")
        .call("deFo42")
        .returns("defo42")
        .call("")
        .returns("")
        .call("Hello, World!")
        .returns("hello, world!")
    )()

    (declarative.function("upper")
        .params("string")
        .returnType(str)
        .call("abc")
        .returns("ABC")
        .call("DEF")
        .returns("DEF")
        .call("deFo42")
        .returns("DEFO42")
        .call("")
        .returns("")
        .call("Hello, World!")
        .returns("HELLO, WORLD!")
    )()