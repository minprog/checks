import check50
import check50.c

@check50.check()
def exists():
    """morse.c exists"""
    check50.exists("morse.c")

@check50.check(exists)
def compiles():
    """morse.c compiles"""
    check50.c.compile("morse.c", lcs50=True)

@check50.check(compiles)
def test_sos():
    """./morse ...---... prints SOS"""
    check50.run("./morse").stdin("...---...").stdout("SOS").exit(0)

@check50.check(compiles)
def test_door():
    """./morse -..------.-. prints DOOR"""
    check50.run("./morse").stdin("-..------.-.").stdout("DOOR").exit(0)

@check50.check(compiles)
def test_ross():
    """./morse .-.------.-. prints ROSS"""
    check50.run("./morse").stdin(".-.---......").stdout("ROSS").exit(0)
