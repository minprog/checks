from checkpy import *
from _default_checks import *
from _helpers import testPytestFail

from typing import Any

checkPytest.nTests = 9

exclude("*")
require(file.name, f"test_{file.name}")

@passed(*allDefaults, hide=False)
def testTests():
    """pytest tests falen bij verschillende incorrecte implementaties"""
    def max_and_index(numbers):
        # a correct implementation of max_and_index
        return max(numbers), numbers.index(max(numbers))

    def items(dictionary):
        # a correct implementation of items
        return list(dictionary.items())

    def list_enumerate(values):
        # a correct implementation of list_enumerate
        return list(enumerate(values))

    correct_max_and_index = max_and_index
    correct_items = items
    correct_list_enumerate = list_enumerate

    def max_and_index(numbers):
        # an incorrect implementation of max_and_index that does nothing
        pass
    testPytestFail(max_and_index, correct_items, correct_list_enumerate)

    def max_and_index(numbers):
        # an incorrect implementation of max_and_index that returns minimum
        return min(numbers), numbers.index(min(numbers))
    testPytestFail(max_and_index, correct_items, correct_list_enumerate)
    
    def max_and_index(numbers):
        # an incorrect implementation of max_and_index that returns wrong index
        return max(numbers), 0
    testPytestFail(max_and_index, correct_items, correct_list_enumerate)
    
    def max_and_index(numbers):
        # an incorrect implementation of max_and_index that returns wrong max
        return 0, numbers.index(max(numbers))
    testPytestFail(max_and_index, correct_items, correct_list_enumerate)
    
    def items(dictionary):
        # an incorrect implementation of items that does nothing
        pass
    testPytestFail(correct_max_and_index, items, correct_list_enumerate)

    def items(dictionary):
        # an incorrect implementation of items with reversed keys and values
        its = []
        for key in dictionary:
            its.append((dictionary[key], key))
        return its
    testPytestFail(correct_max_and_index, items, correct_list_enumerate)

    def list_enumerate(values):
        # an incorrect implementation of list_enumerate that does nothing
        pass
    testPytestFail(correct_max_and_index, correct_items, list_enumerate)

    def list_enumerate(values):
        # an incorrect implementation of list_enumerate that starts at index 1
        enums = []
        for index in range(1, len(values) + 1):
            enums.append((index, values[index - 1]))
        return enums
    testPytestFail(correct_max_and_index, correct_items, list_enumerate)


@passed(testTests, hide=False)
def testMaxAndIndex():
    """max_and_index werkt correct"""
    calls = static.getFunctionCalls()
    for call in calls:
        if call.endswith(("max")):
            raise AssertionError(
                "don't use python's built-in max function for this assignment"
            )
        if call.endswith((".index")):
            raise AssertionError(
                "don't use python's built-in index method for this assignment"
            )

    (declarative.function("max_and_index")
        .params("numbers")
        .returnType(tuple[float, int])
        .call([1, 2, 3, 4])
        .returns((4, 3))
        .call([2])
        .returns((2, 0))
        .call([4, 6, 2, 7, 0])
        .returns((7, 3))
    )()

@passed(testTests, hide=False)
def testItems():
    """items werkt correct"""
    calls = static.getFunctionCalls()
    for call in calls:
        if call.endswith((".items")):
            raise AssertionError(
                "don't use python's built-in items method for this assignment"
            )

    (declarative.function("items")
        .params("dictionary")
        .returnType(list[tuple[Any, Any]])
        .call({1: 3, 2: 4})
        .returns([(1, 3), (2, 4)])
        .call({})
        .returns([])
        .call({1: 2, 2: 2})
        .returns([(1, 2), (2, 2)])
        .call({1: "a", 2: 3.0})
        .returns([(1, "a"), (2, 3.0)])
    )()

@passed(testTests, hide=False)
def testListEnumerate():
    """list_enumerate werkt correct"""
    calls = static.getFunctionCalls()
    for call in calls:
        if call == "enumerate":
            raise AssertionError(
                "don't use python's built-in enumerate method for this assignment"
            )
    
    (declarative.function("list_enumerate")
        .params("values")
        .returnType(list[tuple[int, Any]])
        .call([1, 2, 3])
        .returns([(0, 1), (1, 2), (2, 3)])
        .call([])
        .returns([])
        .call({"hello": 3, 2: 4})
        .returns([(0, "hello"), (1, 2)])
        .call((2, 3, 4))
        .returns([(0, 2), (1, 3), (2, 4)])
    )()

