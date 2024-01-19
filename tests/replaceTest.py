from checkpy import *
from _default_checks import *
from _helpers import testPytestFail
checkPytest.nTests = 4

exclude("*")
require(file.name, f"test_{file.name}")

@passed(*allDefaults, hide=False)
def testTests():
    """pytest tests falen bij verschillende incorrecte implementaties"""
    def replace(string: str, old: str, new: str, count: int=-1) -> str:
        return ""
    testPytestFail(replace)

    def replace(string: str, old: str, new: str, count: int=-1) -> str:
        return string.replace(old, old)
    testPytestFail(replace)

    def replace(string: str, old: str, new: str, count: int=-1) -> str:
        return string.replace(new, old)
    testPytestFail(replace)

    def replace(string: str, old: str, new: str, count: int=-1) -> str:
        return string.replace(old, new, -1)
    testPytestFail(replace)

@passed(testTests, hide=False)
def testFunction():
    """title werkt correct"""
    calls = static.getFunctionCalls()
    for call in calls:
        if call.endswith((".replace")):
            raise AssertionError(
                "don't use python's built-in replace method in this assignment"
            )

    (declarative.function("replace")
        .params("string", "old", "new", "count")
        .returnType(str)
        .call("aaa", "a", "b")
        .returns("aaa".replace("a", "b"))
        .call("ababab", "ab", "cd", 2)
        .returns("ababab".replace("ab", "cd", 2))
        .call("", "1", "2")
        .returns("".replace("1", "2"))
        .call("A - H" * 4 + " Batman!", "A - H", "NaN", -1)
        .returns(("A - H" * 4 + " Batman!").replace("A - H", "NaN"))
    )()