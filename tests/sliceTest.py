from typing_extensions import SupportsIndex
from checkpy import *
from _default_checks import *
from _helpers import testPytestFail
checkPytest.nTests = 8

exclude("*")
require(file.name, f"test_{file.name}")

@passed(*allDefaults, hide=False)
def testTests():
    """pytest tests falen bij verschillende incorrecte implementaties"""
    def slice(string: str, start: int=0, end: int|None=None):
        return ""
    testPytestFail(slice)

    def slice(string: str, start: int=0, end: int|None=None):
        return string[start:end - 1]
    testPytestFail(slice)

    def slice(string: str, start: int=0, end: int|None=None):
        return string[start + 1:end]
    testPytestFail(slice)

@passed(testTests, hide=False)
def testFunction():
    """split werkt correct"""
    slices: tuple[str, slice] = []
    
    class Str(str):
        def __getitem__(self, __key: SupportsIndex | slice) -> str:
            if isinstance(__key, slice):
                slices.append((str(self), __key))

            return super().__getitem__(__key)

    def assertNoSlicing(state: declarative.FunctionState):
        nonlocal slices
        if slices:
            string, s = slices[0]
            raise AssertionError(
                f"gebruik geen slicing bij deze opdracht: {string}[{s.start}:{s.stop}]"
            )
        slices = []

    (declarative.function("slice")
        .params("string", "start", "end")
        .returnType(str)
        .call(Str("abcde"))
        .returns("abcde"[:])
        .do(assertNoSlicing)
        .call(Str("abcde"), 1)
        .returns("abcde"[1:])
        .do(assertNoSlicing)
        .call(Str("abcde"), 1)
        .returns("abcde"[1:])
        .do(assertNoSlicing)
        .call(Str("abcde"), 1, 3)
        .returns("abcde"[1:3])
        .do(assertNoSlicing)
        .call(Str("defghij"), -3)
        .returns("defghij"[-3:])
        .do(assertNoSlicing)
        .call(Str("defghij"), -4, -1)
        .returns("defghij"[-4:-1])
        .do(assertNoSlicing)
        .call(Str("helloworld"), 0, -3)
        .returns("helloworld"[:-3])
        .do(assertNoSlicing)
    )()