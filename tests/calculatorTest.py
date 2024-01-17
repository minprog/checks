from checkpy import *
from _default_checks import *
from _static_analysis import has_call
checkPytest.nTests = 4

exclude("*")
require(file.name, f"test_{file.name}")

@passed(*allDefaults, hide=False)
def testFunction():
    """calculate werkt correct"""
    if has_call("eval", "exec"):
        raise AssertionError("gebruik geen eval() of exec() bij deze opdracht")

    (declarative.function("calculate")
        .params("formula")
        .returnType(float)
        .call("3 + 7")
        .returns(10.0)
        .call("4 / 5")
        .returns(0.8)
        .call("5.5 - -4")
        .returns(9.5)
        .call("-10 * -2")
        .returns(20.0)
    )()

@passed(testFunction, hide=False)
def testProgram():
    """het programma calculator.py werkt correct met invoer en uitvoer"""
    output = outputOf(stdinArgs=["3 + 7"], overwriteAttributes=[("__name__", "__main__")])
    assert output == "10.0\n"
