import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent))

import os
import re
import shutil
from checkpy import *
from _helpers import testPytestFail, runPythonTool
from _default_checks import *
checkPytest.nTests = 4

exclude("*")
require(file.name, "test_cards.py")
includeFromTests("original_card.py")

@passed(*allDefaults, hide=False)
def testAllNewCard():
    """pytest tests testen alle methodes van new_card"""
    exclude("*")
    includeFromTests("log_card.py", "original_card.py")
    require("test_cards.py")

    shutil.copyfile("log_card.py", "new_card.py")

    runPythonTool("pytest")

    if not os.path.exists("log.txt"):
        raise AssertionError("No methods from new_card.py were called in test_cards.py")

    with open("log.txt") as f:
        function_calls = set(l.strip() for l in f.readlines() if l.strip())
        difference = {"suit", "rank", "rank_name", "suit_name"} ^ function_calls
        if difference:
            raise AssertionError(f"The following methods were not called in test_cards.py: {', '.join(difference)}")

@passed(testAllNewCard, hide=False)
def testAllOriginalCard():
    """pytest tests testen alle methodes van original_card"""
    exclude("*")
    includeFromTests("log_card.py")
    require(file.name, "test_cards.py")

    shutil.copyfile("log_card.py", "original_card.py")
    
    runPythonTool("pytest")

    if not os.path.exists("log.txt"):
        raise AssertionError("No methods from new_card.py were called in original_card.py")
    
    with open("log.txt") as f:
        function_calls = set(l.strip() for l in f.readlines() if l.strip())
        difference = {"suit", "rank", "rank_name", "suit_name"} ^ function_calls
        if difference:
            raise AssertionError(f"The following methods were not called in test_cards.py: {', '.join(difference)}")

@passed(testAllOriginalCard, hide=False)
def testOurCard():
    """pytest tests werken ook voor een derde implementatie"""
    exclude("*")
    includeFromTests("our_card.py")
    require(file.name, "test_cards.py")

    shutil.copyfile("our_card.py", "original_card.py")

    result = runPythonTool("pytest")

    # find the number of tests
    nTests = int(re.compile(r"collected (\d+) item").findall(result.stdout)[0])
    
    # find the number of passed tests and assert all tests passed
    nPassed = int(re.compile(r"(\d+) passed in").findall(result.stdout)[0])
    if nPassed != nTests:
        failedTests = re.compile(r"FAILED .*::(.*)").findall(result.stdout)
        formattedFailedTests = "\n  ".join(failedTests)
        raise AssertionError(
            f"Expected all {nTests} test{'s' if nTests != 1 else ''} to pass,"
            f" but {nTests - nPassed} failed:\n  {formattedFailedTests}"
        )

@passed(testOurCard, hide=False)
def testTestsSuit():
    """pytest tests falen bij een foute implementatie van suit()"""
    exclude("*")
    includeFromTests("wrong_card_suit.py")
    require(file.name, "test_cards.py")

    shutil.copyfile("wrong_card_suit.py", "original_card.py")

    assert "FAILED" in runPythonTool("pytest").stdout

@passed(testOurCard, hide=False)
def testTestsRank():
    """pytest tests falen bij een foute implementatie van rank()"""
    exclude("*")
    includeFromTests("wrong_card_rank.py")
    require(file.name, "test_cards.py")

    shutil.copyfile("wrong_card_rank.py", "original_card.py")

    assert "FAILED" in runPythonTool("pytest").stdout

@passed(testOurCard, hide=False)
def testTestsSuitName():
    """pytest tests falen bij een foute implementatie van suit_name()"""
    exclude("*")
    includeFromTests("wrong_card_suit_name.py")
    require(file.name, "test_cards.py")

    shutil.copyfile("wrong_card_suit_name.py", "original_card.py")

    assert "FAILED" in runPythonTool("pytest").stdout

@passed(testOurCard, hide=False)
def testTestsRankName():
    """pytest tests falen bij een foute implementatie van rank_name()"""
    exclude("*")
    includeFromTests("wrong_card_rank_name.py")
    require(file.name, "test_cards.py")

    shutil.copyfile("wrong_card_rank_name.py", "original_card.py")

    assert "FAILED" in runPythonTool("pytest").stdout

# @passed(testTests, hide=False)
# def testFunction():
#     """capitalize werkt correct"""
#     calls = static.getFunctionCalls()
#     for call in calls:
#         if call.endswith((".capitalize")):
#             raise AssertionError(
#                 "don't use python's built-in capitalize method in this assignment"
#             )

#     (declarative.function("capitalize")
#         .params("string")
#         .returnType(str)
#         .call("abc")
#         .returns("Abc")
#         .call("DEF")
#         .returns("Def")
#         .call("deFo42")
#         .returns("Defo42")
#         .call("")
#         .returns("")
#         .call("42hello")
#         .returns("42hello")
#         .call("hello, World!")
#         .returns("Hello, world!")
#     )()