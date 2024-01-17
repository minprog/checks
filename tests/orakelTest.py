from checkpy import *
from _default_checks import *
from _helpers import testPytestFail
checkPytest.nTests = 4

exclude("*")
require(file.name, f"test_{file.name}")

@passed(*allDefaults, hide=False)
def testTests():
    """pytest tests falen bij verschillende incorrecte implementaties"""
    def check_answer(answer: str) -> bool:
        return False
    testPytestFail(check_answer)

    def check_answer(answer: str) -> bool:
        return True
    testPytestFail(check_answer)

    def check_answer(answer: str) -> bool:
        return "42" in answer
    testPytestFail(check_answer)

@passed(testTests, hide=False)
def testFunction():
    """check_answer werkt correct"""
    (declarative.function("check_answer")
        .params("answer")
        .returnType(bool)
        .call("42")
        .returns(True)
        .call("43")
        .returns(False)
        .call("tweeenveertig")
        .returns(True)
        .call("foo")
        .returns(False)
        .call("tweeënveertig")
        .returns(True)
        .call("tweeEnveertIg")
        .returns(True)
    )()

@passed(testFunction, hide=False)
def testProgram():
    """het programma orakel.py werkt correct met invoer en uitvoer"""
    output = outputOf(stdinArgs=[42], overwriteAttributes=[("__name__", "__main__")])
    assert output == "Ja\n"
