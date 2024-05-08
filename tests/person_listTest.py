from checkpy import *
from _default_checks import checkStyle, checkMypy

exclude("*")
require(file.name)

@passed(checkStyle, checkMypy, hide=False)
def testPersonList():
    """PersonList werkt correct"""
    run(
        'person_list = PersonList()',
        'assert person_list.lookup("this_person_does_not_exist") is None',
    )

    run(
        'person_list = PersonList()',
        'alice = Person("alice", 30)',
        'bob = Person("bob", 23)',
        'charlie = Person("charlie", 25)',
        'person_list.add(alice)',
        'person_list.add(charlie)',
        'person_list.add(bob)',
        'assert person_list.lookup("alice") == alice',
        'assert person_list.lookup("bob") == bob',
        'assert person_list.lookup("charlie") == charlie',
        'assert person_list.as_sorted_list() == [alice, bob, charlie]',
        'assert person_list.pop() == alice',
        'assert person_list.as_sorted_list() == [bob, charlie]',
        'assert person_list.remove("charlie") == True',
        'assert person_list.lookup("charlie") is None',
    )


@passed(testPersonList, hide=False)
def testPersonLinkedList():
    """PersonLinkedList werkt correct"""
    run(
        'person_list = PersonLinkedList()',
        'assert person_list.lookup("this_person_does_not_exist") is None',
    )

    run(
        'person_list = PersonLinkedList()',
        'alice = Person("alice", 30)',
        'bob = Person("bob", 23)',
        'charlie = Person("charlie", 25)',
        'person_list.add(alice)',
        'person_list.add(charlie)',
        'person_list.add(bob)',
        'assert person_list.lookup("alice") == alice',
        'assert person_list.lookup("bob") == bob',
        'assert person_list.lookup("charlie") == charlie',
        'assert person_list.as_sorted_list() == [alice, bob, charlie]',
        'assert person_list.pop() == alice',
        'assert person_list.as_sorted_list() == [bob, charlie]',
        'assert person_list.remove("charlie") == True',
        'assert person_list.lookup("charlie") is None',
    )


@passed(testPersonLinkedList, hide=False)
def testPersonDictList():
    """PersonDictList werkt correct"""
    run(
        'person_list = PersonDictList()',
        'assert person_list.lookup("this_person_does_not_exist") is None',
    )

    run(
        'person_list = PersonDictList()',
        'alice = Person("alice", 30)',
        'bob = Person("bob", 23)',
        'charlie = Person("charlie", 25)',
        'person_list.add(alice)',
        'person_list.add(charlie)',
        'person_list.add(bob)',
        'assert person_list.lookup("alice") == alice',
        'assert person_list.lookup("bob") == bob',
        'assert person_list.lookup("charlie") == charlie',
        'assert person_list.as_sorted_list() == [alice, bob, charlie]',
        'assert person_list.pop() == alice',
        'assert person_list.as_sorted_list() == [bob, charlie]',
        'assert person_list.remove("charlie") == True',
        'assert person_list.lookup("charlie") is None',
    )


def run(*statements: str):
    """Helper function that 'exec()'s each statement with shared globals()."""
    env = {}
    name = __name__[:-len("Test")]
    exec(f"from {name} import *", env)
    try:
        for stat in statements:
            exec(stat, env)
    except Exception as e:
        raiseDebugMessage(*statements, failedStatement=stat)


def raiseDebugMessage(*lines: str, failedStatement=None):
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

    name = __name__[:-len("Test")]
    if failedStatement:
        pre = (
            f'This check failed on: {failedStatement}\n' 
            'Run the following code in the terminal to see if you can find out why:\n'
            '$ python3\n'
            f'>>> from {name} import *\n'
        )
    else:
        pre = (
            'This check failed. Run the following code in the terminal to see if you can find out why:\n'
            '$ python3\n'
            f'>>> from {name} import *\n'
        )

    raise AssertionError(pre + "\n".join(fixedLines))