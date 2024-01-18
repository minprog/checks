from checkpy import test, file
from _static_analysis import has_syntax_error, has_string
from _helpers import runPythonTool

import os
import re

__all__ = [
    "checkStyle",
    "checkMypy",
    "checkPytest",
    "allDefaults"
]

@test()
def checkStyle():
    """pycodestyle slaagt"""
    if lineno := has_syntax_error():
        raise AssertionError(f"de code bevat een syntax error op regel {lineno}")

    if has_string("	"):
        raise AssertionError("let op dat je geen tabs gebruikt")
    if has_string("Optional["):
        raise AssertionError("let op dat je niet Optional[...] gebruikt als type hint maar ... | None")
    if has_string("List[", "Tuple[", "Dict[", "Set["):
        raise AssertionError("let op dat je niet List[...] e.d. gebruikt als type hint maar list[...]")

    maxLineLength = os.environ.get("MAX_LINE_LENGTH", 99)
    maxDocLength = os.environ.get("MAX_DOC_LENGTH", 79)

    # run pycodestyle for a couple of basic checks
    result = runPythonTool("pycodestyle", [
        '--select=E101,E112,E113,E115,E116,E117,E501,E502,W505,W291',
        f"--max-line-length={maxLineLength}",
        f"--max-doc-length={maxDocLength}",
        file
    ])

    if result.returncode == 0:
        return

    if "E1" in result.stdout:
        raise AssertionError(f"let op juiste indentatie")

    if "E501" in result.stdout or "W505" in result.stdout:
        raise AssertionError(
            f"regel(s) te lang, code max {maxLineLength} tekens,"
            f" comments max {maxDocLength} tekens\n"
        )

    if "E502" in result.stdout:
        raise AssertionError(f"gebruik tussen haakjes geen \\ om de regel af te breken")

    if "W291" in result.stdout:
        pattern = r'[^:\n]+:(\d+):\d+: W291'
        matches = re.findall(pattern, result.stdout)
        raise AssertionError(
            f"zorg dat er geen spaties aan het eind van een regel"
            f" staan (regel {', '.join(matches)})"
        )

@test()
def checkMypy():
    """mypy --strict --ignore-missing-imports slaagt"""
    result = runPythonTool("mypy", ['--strict', '--ignore-missing-imports', file])

    if result.returncode != 0:
        lines = result.stdout.splitlines()[:-1]
        maxLineLength = 120
        lines = [":".join(line.split(":")[1:])[:maxLineLength] for line in lines]
        lines = ["- line " + line for line in lines]
        raise AssertionError("\n".join(lines))

@test()
def checkPytest():
    """pytest slaagt"""
    nExpectedTests = checkPytest.nTests if hasattr(checkPytest, "nTests") else 5

    result = runPythonTool("pytest")

    # find the number of tests and assert if it's enough
    nTests = int(re.compile(r"collected (\d+) item").findall(result.stdout)[0])
    if nTests < nExpectedTests:
        raise AssertionError(
            f"Expected at least {nExpectedTests} test{'s' if nExpectedTests != 1 else ''}"
            f", but found {nTests} test{'s' if nTests != 1 else ''}"
        )

    # find the number of passed tests and assert all tests passed
    nPassed = int(re.compile(r"(\d+) passed in").findall(result.stdout)[0])
    if nPassed != nTests:
        failedTests = re.compile(r"FAILED .*::(.*)").findall(result.stdout)
        formattedFailedTests = "\n  ".join(failedTests)
        raise AssertionError(
            f"Expected all {nTests} test{'s' if nTests != 1 else ''} to pass,"
            f" but {nTests - nPassed} failed:\n  {formattedFailedTests}"
        )

allDefaults = (checkStyle, checkMypy, checkPytest)
