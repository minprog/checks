from checkpy import *
from _default_checks import *
from _helpers import testPytestFail
checkPytest.nTests = 6

exclude("*")
require(file.name, f"test_{file.name}")

@passed(*allDefaults, hide=False)
def testTests():
    """pytest tests falen bij verschillende incorrecte implementaties"""
    def check_kenteken(kenteken: str) -> bool:
        return True
    testPytestFail(check_kenteken)

    def check_kenteken(kenteken: str) -> bool:
        return False
    testPytestFail(check_kenteken)

    def check_kenteken(kenteken: str) -> bool:
        return len(kenteken) == 6
    testPytestFail(check_kenteken)

    def check_kenteken(kenteken: str) -> bool:
        return kenteken == "13ghj8"
    testPytestFail(check_kenteken)

@passed(testTests, hide=False)
def testFunction():
    """check_kenteken werkt correct"""
    (declarative.function("check_kenteken")
        .params("kenteken")
        .returnType(bool)
        .call("13ghj8")
        .returns(True)
        .call("13ahj8")
        .returns(False)
        .call("J-321-AB")
        .returns(True)
        .call("J-321-ABC")
        .returns(False)
        .call("J-321-A*")
        .returns(False)
        .call("98SgP3")
        .returns(False)
        .call("99-RSTX")
        .returns(True)
    )()

@passed(testFunction, hide=False)
def testProgram():
    """het programma kenteken.py werkt correct met invoer en uitvoer"""
    output = outputOf(stdinArgs=["J-321-AB"], overwriteAttributes=[("__name__", "__main__")])
    assert output == "ja\n"
