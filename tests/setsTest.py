from checkpy import *
from _default_checks import *
from _helpers import testPytestFail
import ast
checkPytest.nTests = 12

exclude("*")
require(file.name, f"test_{file.name}")

@passed(*allDefaults, hide=False)
def testTests():
    """pytest tests falen bij verschillende incorrecte implementaties"""
    def symmetric_difference(set_a: set, set_b: set) -> set:
        return set()
    testPytestFail(symmetric_difference)

    def symmetric_difference(set_a: set, set_b: set) -> set:
        return set_a
    testPytestFail(symmetric_difference)

    def symmetric_difference(set_a: set, set_b: set) -> set:
        return set_b
    testPytestFail(symmetric_difference)

    def symmetric_difference(set_a: set, set_b: set) -> set:
        return set_a - set_b
    testPytestFail(symmetric_difference)

@passed(testTests, hide=False)
def testUnion():
    """union werkt correct"""
    calls = static.getFunctionCalls()
    for call in calls:
        if call.endswith((".union")):
            raise AssertionError(
                "don't use python's built-in union method in this assignment"
            )
    
    # Get union's function definition
    functionDefinitions = static.getAstNodes(ast.FunctionDef)
    functionDefinitions = [f for f in functionDefinitions if f.name == "union"]
    if not functionDefinitions:
        raise AssertionError(
            f"union is not defined in {file.name}"
        )
    unionDef = functionDefinitions[0]

    class UnionVisitor(ast.NodeVisitor):
        def visit_AnnAssign(self, node: ast.AnnAssign):
            # skip Annotated Assignments
            pass

        def visit_BinOp(self, node: ast.BinOp):
            # Assert ast.BitOr is not used outside of ast.AnnAssign
            if type(node.op) == ast.BitOr:
                raise AssertionError(
                    f"don't use python's built-in | operator in this assignment, found on line number: {node.lineno}"
                )

    # Visit each statement in Unions function definition
    for stmt in unionDef.body:
        UnionVisitor().visit(stmt)

    (declarative.function("union")
        .params("set_a", "set_b")
        .returnType(set)
        .call({1, 2}, {3})
        .returns({1, 2, 3})
        .call({1, 2}, {2, 3})
        .returns({1, 2, 3})
        .call({1, 2}, set())
        .returns({1, 2})
        .call(set(), set())
        .returns(set())
        .call({"hello"}, {4, 5})
        .returns({"hello", 4, 5})
    )()

@passed(testTests, hide=False)
def testSymmetricDifference():
    """symmetric_difference werkt correct"""
    calls = static.getFunctionCalls()
    for call in calls:
        if call.endswith((".symmetric_difference")):
            raise AssertionError(
                "don't use python's built-in symmetric_difference method in this assignment"
            )
    
    assert \
        ast.BitXor not in static.AbstractSyntaxTree(), \
        "don't use python's built-in ^ operator in this assignment"
    
    (declarative.function("symmetric_difference")
        .params("set_a", "set_b")
        .returnType(set)
        .call({1, 2, 3}, {2, 3, 4})
        .returns({1, 4})
        .call({1, 2, 3}, {1, 2, 3})
        .returns(set())
        .call({2}, set())
        .returns({2})
        .call(set(), set())
        .returns(set())
        .call({1, "foo"}, {1})
        .returns({"foo"})
    )()