import check50

@check50.check()
def exists():
    """schuifpuzzel.py and hangman.py exist."""
    check50.exists("schuifpuzzel.py", "hangman.py")

@check50.check(exists)
def schuifpuzzel_passes_mypy():
    """schuifpuzzel passes type checks."""
    (check50.run("mypy --strict --ignore-missing-imports schuifpuzzel.py")
        .stdout("Success: no issues found in 1 source file", timeout=10)
        .exit(0))

@check50.check(exists)
def hangman_passes_mypy():
    """hangman passes type checks."""
    (check50.run("mypy --strict --ignore-missing-imports hangman.py")
        .stdout("Success: no issues found in 1 source file", timeout=10)
        .exit(0))
