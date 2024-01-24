from typing_extensions import SupportsIndex
from checkpy import *
from _default_checks import *
from _helpers import testPytestFail
checkPytest.nTests = 4

exclude("*")
require(file.name, f"test_{file.name}")

@passed(*allDefaults, hide=False)
def testTests():
    """pytest tests falen bij verschillende incorrecte implementaties"""
    def value_at(string: str, index: int) -> str:
        return ""
    testPytestFail(value_at)

    def value_at(string: str, index: int) -> str:
        return string[0]
    testPytestFail(value_at)

    def value_at(string: str, index: int) -> str:
        return string[index + 1]
    testPytestFail(value_at)

@passed(testTests, hide=False)
def testFunction():
    """index werkt correct"""
    subscripts: tuple[str, int] = []

    class Str(str):
        def __getitem__(self, __key: SupportsIndex | slice) -> str:
            if isinstance(__key, int):
                subscripts.append((str(self), __key))
            
            return super().__getitem__(__key)

    def assertNoNegativeIndex(state: declarative.FunctionState):
        nonlocal subscripts
        for string, key in subscripts:
            assert key >= 0, f"gebruik geen negatieve indices bij deze opdracht: {string}[{key}]"
        subscripts = []

    (declarative.function("value_at")
        .params("string", "index")
        .returnType(str)
        .call("abcde", 2)
        .returns("abcde"[2])
        .call(Str("abcde"), -1)
        .returns("abcde"[-1])
        .do(assertNoNegativeIndex)
        .call(Str("f"), -1)
        .returns("f"[-1])
        .do(assertNoNegativeIndex)
        .call(Str("abc"), -3)
        .returns("abc"[-3])
        .do(assertNoNegativeIndex)
    )()