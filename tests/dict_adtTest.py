from checkpy import *
from _default_checks import checkStyle
import ast

exclude("*")
require(file.name)

def testDict(dictTypeName: str, only_test_str=False):
    # assert built in dict is not used
    assert ast.Dict not in static.AbstractSyntaxTree(), "don't use Python's built-in dict for this assignment"
    assert ast.DictComp not in static.AbstractSyntaxTree(), "don't use Python's built-in dict for this assignment"
    assert "dict" not in static.getFunctionCalls(), "don't use Python's built-in dict for this assignment"
    
    # get the Dict class from module
    module = getModule()
    assert hasattr(module, dictTypeName), f"expected {dictTypeName} to be defined in {file.name}"

    # test add and get
    run(
        f'd = {dictTypeName}()',
        'd.add("apple", "fruit")',
        'd.add("banana", "fruit")',
        '' if only_test_str else 'd.add(42, "number")',
        'assert d.get("apple") == "fruit"',
        'assert d.get("banana") == "fruit"',
        '' if only_test_str else 'assert d.get(42) == "number"'
    )
    
    # test add update
    run(
        f'd = {dictTypeName}()',
        'd.add("apple", "fruit")',
        'assert d.get("apple") == "fruit"',
        'd.add("apple", "round")',
        'assert d.get("apple") == "round"'
    )

    # test get again
    run(
        f'd = {dictTypeName}()',
        'd.add("apple", "fruit")',
        'assert d.get("apple") == "fruit"',
        'assert d.get("apple") == "fruit"'
    )

    # test get default value
    run(
        f'd = {dictTypeName}()',
        'd.get("unknown", "default") == "default"'
    )

    # test contains
    run(
        f'd = {dictTypeName}()',
        'd.add("apple", "fruit")',
        'assert d.contains("apple"), "expected \'apple\' to be in dictionary"',
        'assert not d.contains("unknown"), "expected \'unknown\' to not be in dictionary"'
    )

    # test remove
    run(
        f'd = {dictTypeName}()',
        'd.add("apple", "fruit")',
        'assert d.remove("apple"), "expected \'apple\' to be removed successfully"',
        'assert not d.contains("apple"), "expected \'apple\' to not be in dictionary after removal"',
        'assert not d.remove("unknown"), "expected \'unknown\' removal to return False"'
    )

@passed(checkStyle, hide=False)
def testListDict():
    """ListDict werkt correct"""
    testDict("ListDict")

@passed(checkStyle, hide=False)
def testStrDict():
    """StrDict werkt correct"""
    testDict("StrDict", only_test_str=True)

@passed(checkStyle, hide=False)
def testHashStrDict():
    """HashStrDict werkt correct"""
    testDict("HashStrDict", only_test_str=True)

@passed(checkStyle, hide=False)
def testHashDict():
    """HashDict werkt correct"""
    testDict("HashDict")

def run(*statements: str):
    """Helper function that 'exec()'s each statement with shared globals()."""
    env = {}
    exec(f"from {file.name.rstrip(".py")} import *", env)
    try:
        for stat in statements:
            exec(stat, env)
    except:
        raiseDebugMessage(*statements)

def raiseDebugMessage(*lines: str):
    """
    Helper function that formats each line as if it were fed to Python's repl.
    Then raises an AssertionError with the formatted message.
    """
    def fixLine(line: str) -> str:
        line = line.rstrip("\n")

        if line.startswith(" "):
            return "... " + line
        if not line.startswith(">>> "):
            return ">>> " + line
        return line

    # break-up multi-line statements
    actualLines = []
    for line in lines:
        actualLines.extend([l for l in line.split("\n") if l])

    # prepend >>> and ... (what you'd see in the REPL)
    # replace any "assert " statements with "True" on the next line
    fixedLines = [fixLine(l) for l in actualLines]

    pre = (
        'This check failed. Run the following code in the terminal to find out why:\n'
        '$ python3\n'
        f'>>> from {file.name.rstrip(".py")} import *\n'
    )

    raise AssertionError(pre + "\n".join(fixedLines))