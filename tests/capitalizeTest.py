from checkpy import *
from _default_checks import *
from _helpers import testPytestFail
checkPytest.nTests = 3

exclude("*")
require(file.name, f"test_{file.name}")

@passed(*allDefaults, hide=False)
def testTests():
    """pytest tests falen bij verschillende incorrecte implementaties"""
    def capitalize(string: str) -> str:
        return "Foo"
    testPytestFail(capitalize)

    def capitalize(string: str) -> str:
        return string
    testPytestFail(capitalize)

@passed(testTests, hide=False)
def testFunction():
    """capitalize werkt correct"""
    calls = static.getFunctionCalls()
    for call in calls:
        if call.endswith((".capitalize")):
            raise AssertionError(
                "don't use python's built-in capitalize method in this assignment"
            )

    (declarative.function("capitalize")
        .params("string")
        .returnType(str)
        .call("abc")
        .returns("Abc")
        .call("DEF")
        .returns("Def")
        .call("deFo42")
        .returns("Defo42")
        .call("")
        .returns("")
        .call("42hello")
        .returns("42hello")
        .call("hello, World!")
        .returns("Hello, world!")
    )()