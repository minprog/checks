from checkpy import *
# from _default_checks import checkStyle, checkMypy

exclude("*")
require(file.name)

@passed(checkStyle, checkMypy, hide=False)
def testEnqueue():
    """enqueue voegt elementen toe aan de achterkant van de Queue"""
    run(
        'q = Queue()',
        'assert q.enqueue(1) is None, "expected enqueue() to return None"',
        'q.enqueue("a")',
        'q.enqueue(3.5)',
        'assert q.size() == 3, "expected size() to be 3 after enqueueing 3 elements"',
        'assert q.peek() == 1, "expected the first enqueued element to be at the front"',
    )

@passed(testEnqueue, hide=False)
def testDequeue():
    """dequeue verwijdert en geeft het voorste element terug, in first-in-first-out volgorde"""
    run(
        'q = Queue()',
        'q.enqueue(3)',
        'q.enqueue(1)',
        'q.enqueue("two")',
        'assert q.dequeue() == 3',
        'assert q.dequeue() == 1',
        'q.enqueue(4)',
        'assert q.dequeue() == "two"',
        'assert q.dequeue() == 4',
        'assert q.size() == 0, "expected the queue to be empty after dequeueing all elements"',
    )

    run(
        'q = Queue()',
        'try:\n    q.dequeue()\nexcept AssertionError:\n    pass\nelse:\n    raise AssertionError("expected dequeue() on an empty Queue to raise an AssertionError")',
        'q.enqueue(1)',
        'q.dequeue()',
        'try:\n    q.dequeue()\nexcept AssertionError:\n    pass\nelse:\n    raise AssertionError("expected dequeue() on an empty Queue to raise an AssertionError")',
    )

@passed(testEnqueue, hide=False)
def testSize():
    """size geeft het aantal elementen in de Queue terug"""
    run(
        'q = Queue()',
        'assert q.size() == 0, "expected a new Queue to have size 0"',
        'q.enqueue("a")',
        'assert q.size() == 1',
        'q.enqueue("a")',
        'q.enqueue(None)',
        'assert q.size() == 3',
        'assert q.size() == 3, "expected size() to not change the Queue"',
        'q.dequeue()',
        'assert q.size() == 2',
    )

@passed(testEnqueue, hide=False)
def testPeek():
    """peek geeft het voorste element terug zonder het te verwijderen"""
    run(
        'q = Queue()',
        'q.enqueue(5)',
        'q.enqueue(6)',
        'assert q.peek() == 5',
        'assert q.peek() == 5, "expected peek() to not remove the element"',
        'assert q.size() == 2, "expected peek() to not change the size of the Queue"',
        'q.dequeue()',
        'assert q.peek() == 6',
    )

@passed(testDequeue, testSize, hide=False)
def testEmpty():
    """empty verwijdert alle elementen uit de Queue"""
    run(
        'q = Queue()',
        'q.empty()',
        'assert q.size() == 0',
        'q.enqueue(1)',
        'q.enqueue(2)',
        'q.enqueue(3)',
        'q.empty()',
        'assert q.size() == 0, "expected the Queue to be empty after empty()"',
        'q.enqueue(4)',
        'assert q.size() == 1',
        'assert q.peek() == 4, "expected only the element enqueued after empty() to remain"',
        'assert q.dequeue() == 4',
    )

def run(*statements: str):
    """Helper function that 'exec()'s each statement with shared globals()."""
    env = {}
    exec(f"from {file.name.rstrip('.py')} import *", env)
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
    fixedLines = [fixLine(l) for l in actualLines]

    pre = (
        'This check failed. Run the following code in the terminal to find out why:\n'
        '$ python3\n'
        f'>>> from {file.name.rstrip(".py")} import *\n'
    )

    raise AssertionError(pre + "\n".join(fixedLines))
