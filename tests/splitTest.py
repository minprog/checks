from checkpy import *
from _default_checks import *
from _helpers import testPytestFail
checkPytest.nTests = 6

exclude("*")
require(file.name, f"test_{file.name}")

@passed(*allDefaults, hide=False)
def testTests():
    """pytest tests falen bij verschillende incorrecte implementaties"""
    def split(string: str, sep: str, maxsplit: int=-1) -> list[str]:
        return []
    testPytestFail(split)

    def split(string: str, sep: str, maxsplit: int=-1) -> list[str]:
        return string.split(sep, maxsplit - 1) 
    testPytestFail(split)

    def split(string: str, sep: str, maxsplit: int=-1) -> list[str]:
        return string.split("a", maxsplit) 
    testPytestFail(split)

@passed(testTests, hide=False)
def testFunction():
    """split werkt correct"""
    calls = static.getFunctionCalls()
    for call in calls:
        if call.endswith((".split")):
            raise AssertionError(
                "don't use python's built-in split method in this assignment"
            )

    (declarative.function("split")
        .params("string", "sep", "maxsplit")
        .returnType(list[str])
        .call("a,b", ",")
        .returns("a,b".split(","))
        .call("a:,b:,c", ":,")
        .returns("a:,b:,c".split(":,"))
        .call("10101001", "0")
        .returns("10101001".split("0"))
        .call("10101001", "0", 3)
        .returns("10101001".split("0", 3))
        .call("a b c d", " ", 2)
        .returns("a b c d".split(" ", 2))
        .call("", ",")
        .returns([""])
    )()