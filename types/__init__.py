import check50

@check50.check()
def exists():
    """mario.py, readability.py and dna.py exist."""
    check50.exists("mario.py", "readability.py", "dna.py")

@check50.check(exists)
def mario_passes_mypy():
    """mario passes type checks."""
    (check50.run("mypy --strict mario.py")
        .stdout("Success: no issues found in 1 source file")
        .exit(0))

@check50.check(exists)
def readability_passes_mypy():
    """readability passes type checks."""
    (check50.run("mypy --strict readability.py")
        .stdout("Success: no issues found in 1 source file")
        .exit(0))

@check50.check(exists)
def dna_passes_mypy():
    """dna passes type checks."""
    (check50.run("mypy --strict dna.py")
        .stdout("Success: no issues found in 1 source file")
        .exit(0))
