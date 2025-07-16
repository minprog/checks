import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent))

import os
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
    """pytest tests test alle methodes van new_card"""
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

@passed(*allDefaults, hide=False)
def testAllOriginalCard():
    """pytest tests test alle methodes van original_card"""
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


# @passed(*allDefaults, hide=False)
# def testTests():
#     """pytest tests falen bij verschillende incorrecte implementaties"""
#     def capitalize(string: str) -> str:
#         return "Foo"
#     testPytestFail(capitalize)

#     def capitalize(string: str) -> str:
#         return string
#     testPytestFail(capitalize)

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