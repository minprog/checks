from checkpy import *
from _default_checks import *
from _helpers import testPytestFail
checkPytest.nTests = 6

exclude("*")
require(file.name, f"test_{file.name}")

@passed(*allDefaults, hide=False)
def testTests():
    """pytest tests falen bij verschillende incorrecte implementaties"""
    def find(string: str, sub: str, start: int|None=None, end: int|None=None) -> int:
        return -1
    testPytestFail(find)

    def find(string: str, sub: str, start: int|None=None, end: int|None=None) -> int:
        return string.find(sub, start, end) + 1
    testPytestFail(find)

    def find(string: str, sub: str, start: int|None=None, end: int|None=None) -> int:
        return string.find(sub)
    testPytestFail(find)

@passed(testTests, hide=False)
def testFunction():
    """find werkt correct"""
    calls = static.getFunctionCalls()
    for call in calls:
        if call.endswith((".find")):
            raise AssertionError(
                "don't use python's built-in find method in this assignment"
            )

    (declarative.function("find")
        .params("string", "sub", "start", "end")
        .returnType(int)
        .call("abc", "a")
        .returns("abc".find("a"))
        .call("abc", "d")
        .returns("abc".find("d"))
        .call("10101001001", "00")
        .returns("10101001001".find("00"))
        .call("", "hello")
        .returns("".find("hello"))
        .call("10101001001", "00", 7)
        .returns("10101001001".find("00", 7))
        .call("hello world hello world", "el", 6, 15)
        .returns("hello world hello world".find("el", 6, 15))
        .call("abcdef", "d", -100, -2)
        .returns("abcdef".find("d", -100, -2))
        .call("a", "a", -100, 100)
        .returns("a".find("a", -100, 100))
        .call("a", "a", 50, -50)
        .returns("a".find("a", 50, -50))
    )()