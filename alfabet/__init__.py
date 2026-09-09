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
def test_usage_geen_argumenten():
    """zonder argumenten print: Usage: ./alfabet <woord1> <woord2>"""
    check_usage("./alfabet")

@check50.check(compiles)
def test_usage_een_argument():
    """met één argument print: Usage: ./alfabet <woord1> <woord2>"""
    check_usage("./alfabet taylor")

@check50.check(compiles)
def test_usage_te_veel_argumenten():
    """met drie argumenten print: Usage: ./alfabet <woord1> <woord2>"""
    check_usage("./alfabet taylor lana olivia")

@check50.check(compiles)
def test_taylor_lana():
    """taylor en lana als argumenten geeft lana"""
    check50.run("./alfabet taylor lana").stdout("lana").exit(0)

@check50.check(compiles)
def test_shark_sword():
    """shark en sWoRd als argumenten geeft shark"""
    check50.run("./alfabet shark sWoRd").stdout("shark").exit(0)

@check50.check(compiles)
def test_daantje_daan():
    """Daantje en Daan als argumenten geeft Daan"""
    check50.run("./alfabet Daantje Daan").stdout("Daan").exit(0)

@check50.check(compiles)
def test_amanda_amanda():
    """amanda en Amanda als argumenten geeft No need to decide!"""
    check50.run("./alfabet amanda Amanda").stdout("[Nn]o need to decide", str_output="No need to decide!").exit(0)


def check_usage(command):
    """run command and expect the usage message plus exit code 1"""
    process = check50.run(command)
    out = process.stdout().strip()

    if out != "Usage: ./alfabet <woord1> <woord2>":
        raise check50.Failure(f"expected Usage: ./alfabet <woord1> <woord2>, but found {out}")

    check50.log("checking that program exited with status 1...")
    if process.exitcode != 1:
        raise check50.Failure(f"expected exit code 1, not {process.exitcode}")
