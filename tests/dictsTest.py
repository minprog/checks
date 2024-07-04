from checkpy import *
from _default_checks import *
from _helpers import testPytestFail

checkPytest.nTests = 11

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

    def update(dict_a, dict_b):
        # a correct implementation of update
        dict_a.update(dict_b)

    correct_get = get
    correct_values = values
    correct_update = update

    def update(dict_a, dict_b):
        # an incorrect implementation of update that does nothing
        pass
    testPytestFail(correct_get, update, correct_values)

    def update(dict_a, dict_b):
        # an incorrect implementation of update that updates the wrong dict
        dict_b.update(dict_a)
    testPytestFail(correct_get, update, correct_values)

    def get(dictionary, key, default_value=None):
        # an incorrect implementation of get that does nothing
        pass
    testPytestFail(get, correct_update, correct_values)

    def get(dictionary, key, default_value=None):
        # an incorrect implementation of get that always gets default_value
        return default_value
    testPytestFail(get, correct_update, correct_values)

    def values(dictionary):
        # an incorrect implementation of values that does nothing
        pass
    testPytestFail(correct_get, correct_update, values)

    def values(dictionary):
        # an incorrect implementation of values that returns the keys
        return list(dictionary)
    testPytestFail(correct_get, correct_update, values)


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

