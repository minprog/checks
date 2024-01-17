from checkpy import include, file
import subprocess
import inspect
from typing import Callable

def testPytestFail(*functions: list[Callable]):
    """Test whether pytest gives an AssertionError with given functions."""
    # Open a new sandbox
    include("*")

    # Get src of all functions
    sources: list[str] = []
    for func in functions:
        src = inspect.getsource(func)

        # rm indentation
        lines = src.split("\n")
        indentLevel = len(lines[0]) - len(lines[0].lstrip())
        lines = [line[indentLevel:] for line in lines]
        src = "\n".join(lines)

        sources.append(src)

    # Write src to `checkpy.file.name`
    src = "\n".join(sources)
    with open(file.name, "w") as f:
        f.write(src + "\n")

    # Assert pytest raises an AssertionError
    if "FAILED" not in runPythonTool("pytest").stdout:
        raise AssertionError(
            "Expected the following implementation to fail the pytest tests:\n\n" + src
        )

def runPythonTool(tool: str, optionalArgs: list[str]=[]) -> subprocess.CompletedProcess:
    # run tool
    try:
        result = subprocess.run(
            [tool] + optionalArgs,
            capture_output=True,
            universal_newlines=True
        )
        return result
    except FileNotFoundError:
        pass

    # check if python3's pip knows of tool
    isToolInstalled = subprocess.run(
        ["python3", "-m", "pip", "show", tool],
        capture_output=True,
        universal_newlines=True
    ).returncode == 0

    # if not, raise AssertionError
    if not isToolInstalled:
        raise AssertionError(
            f"{tool} is not installed."
            f" You can install {tool} via: python3 -m pip install {tool}"
        )

    # run tool via python3 -m tool
    return subprocess.run(
        ["python3", "-m", tool] + optionalArgs,
        capture_output=True,
        universal_newlines=True
    )