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
def test_woord1():
    """input van Equal en renal print equal"""
    check50.run("./klinkers").stdin("Equal").stdin("renal").stdout("equal").exit(0)

@check50.check(compiles)
def test_woord2():
    """input van Retina en AwesOmE print awesome"""
    check50.run("./klinkers").stdin("Retina").stdin("AwesOmE").stdout("awesome").exit(0)

@check50.check(compiles)
def test_equal():
    """input van aye en abide print aye\\nabide"""
    check50.run("./klinkers").stdin("aye").stdin("abide").stdout("aye\nabide").exit(0)
