import check50
import check50.c

@check50.check()
def exists():
    """hoofdletters.c exists"""
    check50.exists("hoofdletters.c")

@check50.check(exists)
def compiles():
    """hoofdletters.c compiles"""
    check50.c.compile("hoofdletters.c", lcs50=True)

@check50.check(compiles)
def test_1_hoofdletter():
    """"Er zijn geen goede schrijvers." als invoer print: 1 woord met een hoofdletter"""
    check50.run("./hoofdletters").stdin("Er zijn geen goede schrijvers.").stdout("1 woord met een hoofdletter").exit(0)

@check50.check(compiles)
def test_2_hoofdletters():
    """"Het leven op zondag begon zonder Onrust." als invoer print: 2 woorden met een hoofdletter"""
    check50.run("./hoofdletters").stdin("Het leven op zondag begon zonder Onrust.").stdout("2 woorden met een hoofdletter").exit(0)

@check50.check(compiles)
def test_2_hoofdletters_met_streep():
    """"Obi-Wan Kenobi nam zijn taak vrij serieus" als invoer print: 2 woorden met een hoofdletter"""
    check50.run("./hoofdletters").stdin("Obi-Wan Kenobi nam zijn taak vrij serieus").stdout("2 woorden met een hoofdletter").exit(0)

@check50.check(compiles)
def test_0_hoofdletters():
    """"ergens heeft het ook wel wat" als invoer print: 0 woorden met een hoofdletter"""
    check50.run("./hoofdletters").stdin("ergens heeft het ook wel wat").stdout("0 woorden met een hoofdletter").exit(0)
