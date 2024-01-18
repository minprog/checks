from _ast import Call
from typing import Any
from checkpy import *
from _default_checks import *
from _helpers import testPytestFail
checkPytest.nTests = 3

exclude("*")
require(file.name, f"test_{file.name}")

@passed(*allDefaults, hide=False)
def testTests():
    """pytest tests falen bij verschillende incorrecte implementaties"""
    def isalpha(string: str) -> bool:
        return True
    testPytestFail(isalpha)

    def isalpha(string: str) -> bool:
        return False
    testPytestFail(isalpha)

    def isalpha(string: str) -> bool:
        return string in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    testPytestFail(isalpha)

@passed(testTests, hide=False)
def testFunction():
    """isalpha werkt correct"""
    calls = static.getFunctionCalls()
    for call in calls:
        if call.endswith(".isalpha"):
            raise AssertionError(
                "don't use python's built-in isalpha method in this assignment"
            )

    (declarative.function("isalpha")
        .params("string")
        .returnType(bool)
        .call("cba")
        .returns(True)
        .call("AbC")
        .returns(True)
        .call("huH7")
        .returns(False)
        .call("")
        .returns(False)
        .call("hello world")
        .returns(False)
        .call("foo!")
        .returns(False)
    )()
