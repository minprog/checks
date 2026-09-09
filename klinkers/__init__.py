import check50
import check50.c

@check50.check()
def exists():
    """klinkers.c exists"""
    check50.exists("klinkers.c")

@check50.check(exists)
def compiles():
    """klinkers.c compiles"""
    check50.c.compile("klinkers.c", lcs50=True)

@check50.check(compiles)
def test_usage_geen_argumenten():
    """zonder argumenten print: Usage: ./klinkers <woord1> <woord2>"""
    check_usage("./klinkers")

@check50.check(compiles)
def test_usage_een_argument():
    """met één argument print: Usage: ./klinkers <woord1> <woord2>"""
    check_usage("./klinkers aye")

@check50.check(compiles)
def test_usage_te_veel_argumenten():
    """met drie argumenten print: Usage: ./klinkers <woord1> <woord2>"""
    check_usage("./klinkers aye abide equal")

@check50.check(compiles)
def test_woord1():
    """Equal en renal als argumenten print equal"""
    check50.run("./klinkers Equal renal").stdout("equal").exit(0)

@check50.check(compiles)
def test_woord2():
    """Retina en AwesOmE als argumenten print awesome"""
    check50.run("./klinkers Retina AwesOmE").stdout("awesome").exit(0)

@check50.check(compiles)
def test_equal():
    """aye en abide als argumenten print aye\\nabide"""
    check50.run("./klinkers aye abide").stdout("aye\nabide").exit(0)


def check_usage(command):
    """run command and expect the usage message plus exit code 1"""
    process = check50.run(command)
    out = process.stdout().strip()

    if out != "Usage: ./klinkers <woord1> <woord2>":
        raise check50.Failure(f"expected Usage: ./klinkers <woord1> <woord2>, but found {out}")

    check50.log("checking that program exited with status 1...")
    if process.exitcode != 1:
        raise check50.Failure(f"expected exit code 1, not {process.exitcode}")
