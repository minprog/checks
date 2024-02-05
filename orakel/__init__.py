import check50
import check50.c
import check50.internal

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)

@check50.check()
def exists():
    """orakel.c exists"""
    check50.exists("orakel.c")

@check50.check(exists)
def compiles():
    """orakel.c compiles"""
    check50.c.compile("orakel.c", lcs50=True)

@check50.check(compiles)
def test_orakel_42():
    """input of 42 prints Ja"""
    check50.run("./orakel").stdin("42").stdout("Ja").exit(0)

@check50.check(compiles)
def test_orakel_41():
    """input of 41 prints Nee"""
    check50.run("./orakel").stdin("41").stdout("Nee").exit(0)

@check50.check(compiles)
def test_orakel_tweeenveertig():
    """input of tweeenveertig prints Ja"""
    check50.run("./orakel").stdin("tweeenveertig").stdout("Ja").exit(0)

@check50.check(compiles)
def test_orakel_tweeenveertig2():
    """input of tweeënveertig prints Ja"""
    check50.run("./orakel").stdin("tweeënveertig").stdout("Ja").exit(0)

@check50.check(compiles)
def test_orakel_dertig():
    """input of dertig prints Nee"""
    check50.run("./orakel").stdin("dertig").stdout("Nee").exit(0)

