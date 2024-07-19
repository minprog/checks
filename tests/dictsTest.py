from checkpy import *
from _default_checks import *
from _helpers import testPytestFail

import ast
from typing import Any

checkPytest.nTests = 15

exclude("*")
require(file.name, f"test_{file.name}")

@passed(*allDefaults, hide=False)
def testTests():
    """pytest tests falen bij verschillende incorrecte implementaties"""
    def get(dictionary, key, default_value=None):
        # a correct implementation of get
        return dictionary.get(key, default_value)

    def values(dictionary):
        # a correct implementation of values
        return list(dictionary.values())

    def count(values):
        # a correct implementation of count
        from collections import Counter
        return dict(Counter.fromkeys(values))

    def update(dict_a, dict_b):
        # a correct implementation of update
        dict_a.update(dict_b)

    correct_get = get
    correct_values = values
    correct_count = count
    correct_update = update

    def update(dict_a, dict_b):
        # an incorrect implementation of update that does nothing
        pass
    testPytestFail(correct_get, correct_count, update, correct_values)

    def update(dict_a, dict_b):
        # an incorrect implementation of update that updates the wrong dict
        dict_b.update(dict_a)
    testPytestFail(correct_get, correct_count, update, correct_values)

    def get(dictionary, key, default_value=None):
        # an incorrect implementation of get that does nothing
        pass
    testPytestFail(get, correct_count, correct_update, correct_values)

    def get(dictionary, key, default_value=None):
        # an incorrect implementation of get that always gets default_value
        return default_value
    testPytestFail(get, correct_count, correct_update, correct_values)

    def count(values):
        # an incorrect implementation of count that does nothing
        pass
    testPytestFail(correct_get, count, correct_update, correct_values)

    def count(values):
        # an incorrect implementation of count that counts only one element
        if values:
            return {values[0]: 1}
        return {}
    testPytestFail(correct_get, count, correct_update, correct_values)
    
    def count(values):
        # an incorrect implementation of count that can only count up to 1
        counts = {}
        for value in values:
            counts[value] = 1
        return counts
    testPytestFail(correct_get, count, correct_update, correct_values)

    def values(dictionary):
        # an incorrect implementation of values that does nothing
        pass
    testPytestFail(correct_get, correct_count, correct_update, values)

    def values(dictionary):
        # an incorrect implementation of values that returns the keys
        return list(dictionary)
    testPytestFail(correct_get, correct_count, correct_update, values)


@passed(testTests, hide=False)
def testGet():
    """get werkt correct"""
    calls = static.getFunctionCalls()
    for call in calls:
        if call.endswith((".get")):
            raise AssertionError(
                "don't use python's built-in get method for this assignment"
            )
    
    (declarative.function("get")
        .params("dictionary", "key", "default_value")
        .call({1: 2, 3: 4}, 1)
        .returns(2)
        .call({1: 2, 3: 4}, 0)
        .returns(None)
        .call({1: 2, 3: 4}, 0, 0)
        .returns(0)
        .call({}, 1)
        .returns(None)
    )()

@passed(testTests, hide=False)
def testValues():
    """values werkt correct"""
    calls = static.getFunctionCalls()
    for call in calls:
        if call.endswith((".values")):
            raise AssertionError(
                "don't use python's built-in values method for this assignment"
            )

    (declarative.function("values")
        .params("dictionary")
        .returnType(list)
        .call({1: 2, 3: 4})
        .returns([2, 4])
        .call({})
        .returns([])
        .call({0: 2, 1 : 2})
        .returns([2, 2])
    )()

@passed(testTests, hide=False)
def testCount():
    """count werkt correct"""
    for imp in static.getAstNodes(ast.Import):
        for alias in imp.names:
            if alias.name == "collections":
                raise AssertionError("don't use the collections module in this assignment")

    for imp in static.getAstNodes(ast.ImportFrom):
        if imp.module == "collections":
            raise AssertionError("don't use the collections module in this assignment")

    (declarative.function("count")
        .params("values")
        .returnType(dict[Any, int])
        .call([])
        .returns({})
        .call([1, 2, 3, 4, 5])
        .returns({1: 1, 2: 1, 3: 1, 4: 1, 5: 1})
        .call([1, 2, 2, 3, 3, 3, 4, 4, 4, 4])
        .returns({1: 1, 2: 2, 3: 3, 4: 4})
        .call([1, 'a', 1, 'a', 2.5, 'b', 2.5])
        .returns({1: 2, 'a': 2, 2.5: 2, 'b': 1})
    )


@passed(testTests, hide=False)
def testUpdate():
    """update werkt correct"""
    calls = static.getFunctionCalls()
    for call in calls:
        if call.endswith((".update")):
            raise AssertionError(
                "don't use python's built-in update method for this assignment"
            )
    
    def assertEqual(d1, d2):
        assert d1 == d2

    (declarative.function("update")
        .params("dict_a", "dict_b")
        .returnType(None)
        .call(a := {0: 1}, {1: 2})
        .do(lambda fs: assertEqual(a, {0: 1, 1: 2}))
        .call(b := {0: 1}, {0: 1})
        .do(lambda fs: assertEqual(b, {0: 1}))
        .call(c := {0: 1}, {0: 2})
        .do(lambda fs: assertEqual(c, {0: 2}))
        .call(d := {0: 1}, {})
        .do(lambda fs: assertEqual(d, {0: 1}))
    )()

