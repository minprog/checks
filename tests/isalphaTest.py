from checkpy import *
from _default_checks import *
from _helpers import testPytestFail
checkPytest.nTests = 9

exclude("*")
require(file.name, f"test_{file.name}")

@passed(*allDefaults, hide=False)
def testTests():
    """pytest tests falen bij verschillende incorrecte implementaties"""
    # isalpha tests
    def isalpha(string: str) -> bool:
        return True
    def islower(string: str) -> bool:
        return string.islower()
    def isupper(string: str) -> bool:
        return string.isupper()
    testPytestFail(isalpha, islower, isupper)

    def isalpha(string: str) -> bool:
        return False
    testPytestFail(isalpha, islower, isupper)

    def isalpha(string: str) -> bool:
        return string in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    testPytestFail(isalpha, islower, isupper)

    # islower tests
    def isalpha(string: str) -> bool:
        return string.isalpha()
    def islower(string: str) -> bool:
        return True
    def isupper(string: str) -> bool:
        return string.isupper()
    testPytestFail(isalpha, islower, isupper)

    def islower(string: str) -> bool:
        return False
    testPytestFail(isalpha, islower, isupper)

    def islower(string: str) -> bool:
        return string in "abcdefghijklmnopqrstuvwxyz"
    testPytestFail(isalpha, islower, isupper)
    
    # isupper tests
    def isalpha(string: str) -> bool:
        return string.isalpha()
    def islower(string: str) -> bool:
        return string.islower()
    def isupper(string: str) -> bool:
        return True
    testPytestFail(isalpha, islower, isupper)

    def isupper(string: str) -> bool:
        return False
    testPytestFail(isalpha, islower, isupper)

    def isupper(string: str) -> bool:
        return string in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    testPytestFail(isalpha, islower, isupper)


@passed(testTests, hide=False)
def testFunction():
    """isalpha, islower en isupper werken correct"""
    calls = static.getFunctionCalls()
    for call in calls:
        if call.endswith((".isalpha", ".islower", ".isupper")):
            raise AssertionError(
                "don't use python's built-in isalpha/islower/isupper methods in this assignment"
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

    (declarative.function("islower")
        .params("string")
        .returnType(bool)
        .call("cba")
        .returns(True)
        .call("AbC")
        .returns(False)
        .call("huh7")
        .returns(True)
        .call("")
        .returns(False)
        .call("hello world")
        .returns(True)
        .call("foo!")
        .returns(True)
    )()

    (declarative.function("isupper")
        .params("string")
        .returnType(bool)
        .call("cba")
        .returns(False)
        .call("AbC")
        .returns(False)
        .call("ABC")
        .returns(True)
        .call("huH7")
        .returns(False)
        .call("")
        .returns(False)
        .call("HELLO WORLD")
        .returns(True)
        .call("FOO!")
        .returns(True)
    )()
