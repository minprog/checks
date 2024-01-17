from checkpy import *
from _default_checks import *
from _helpers import testPytestFail
checkPytest.nTests = 4

exclude("*")
require(file.name, f"test_{file.name}")

@passed(*allDefaults, hide=False)
def testTests():
    """pytest tests falen bij verschillende incorrecte implementaties"""
    def convert(name: str) -> str:
        return "open_file"
    testPytestFail(convert)

    def convert(name: str) -> str:
        return "openFile"
    testPytestFail(convert)

    def convert(name: str) -> str:
        if name == "open_file":
            return "openFile"
        return "open_file"
    testPytestFail(convert)

@passed(testTests, hide=False)
def testFunction():
    """convert werkt correct"""
    (declarative.function("convert")
        .params("name")
        .returnType(str)
        .call("openFile")
        .returns("open_file")
        .call("close_file")
        .returns("closeFile")
        .call("mixed_useCases")
        .returns("mixed_use_cases")
        .call("coMpLeTeChAoS")
        .returns("co_mp_le_te_ch_ao_s")
    )()

@passed(testFunction, hide=False)
def testProgram():
    """het programma camelcase.py werkt correct met invoer en uitvoer"""
    output = outputOf(stdinArgs=["close_file"], overwriteAttributes=[("__name__", "__main__")])
    assert output == "closeFile\n"
