from checkpy import *
from _default_checks import *
from _helpers import testPytestFail
checkPytest.nTests = 4

exclude("*")
require(file.name, f"test_{file.name}")

@passed(*allDefaults, hide=False)
def testTests():
    """pytest tests falen bij verschillende incorrecte implementaties"""
    def join(string: str, items: list[str]) -> str:
        return ""
    testPytestFail(join)

    def join(string: str, items: list[str]) -> str:
        return "".join(items)
    testPytestFail(join)

    def join(string: str, items: list[str]) -> str:
        return string + string.join(items)
    testPytestFail(join)

@passed(testTests, hide=False)
def testFunction():
    """join werkt correct"""
    calls = static.getFunctionCalls()
    for call in calls:
        if call.endswith((".join")):
            raise AssertionError(
                "don't use python's built-in join method in this assignment"
            )

    (declarative.function("join")
        .params("string", "items")
        .returnType(str)
        .call(",", ["a", "b", "c"])
        .returns(",".join(["a", "b", "c"]))
        .call("-", [""])
        .returns("-".join([""]))
        .call("foo", ["a"])
        .returns("foo".join(["a"]))
        .call("", ["foo", "bar", "world"])
        .returns("".join(["foo", "bar", "world"]))
        .call(", ", ["hello", "world!"])
        .returns(", ".join(["hello", "world!"]))
    )()
