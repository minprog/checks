import check50
import check50.c

@check50.check()
def exists():
    """alfabet.c exists"""
    check50.exists("alfabet.c")

@check50.check(exists)
def compiles():
    """alfabet.c compiles"""
    check50.c.compile("alfabet.c", lcs50=True)

@check50.check(compiles)
def test_taylor_lana():
    """input van taylor en lana geeft lana"""
    check50.run("./alfabet").stdin("taylor").stdin("lana").stdout("lana").exit(0)

@check50.check(compiles)
def test_shark_sword():
    """input van shark en sWoRd geeft shark"""
    check50.run("./alfabet").stdin("shark").stdin("sWoRd").stdout("shark").exit(0)

@check50.check(compiles)
def test_daantje_daan():
    """input van Daantje en Daan geeft Daan"""
    check50.run("./alfabet").stdin("Daantje").stdin("Daan").stdout("Daan").exit(0)

@check50.check(compiles)
def test_amanda_amanda():
    """input van amanda en Amanda geeft No need to decide!"""
    check50.run("./alfabet").stdin("amanda").stdin("Amanda").stdout("[Nn]o need to decide", str_output="No need to decide!").exit(0)