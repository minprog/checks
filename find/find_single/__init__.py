import check50
import check50.c

@check50.check()
def exists():
    """find.c exists."""
    check50.exists("find.c")

@check50.check(exists)
def compiles():
    """find.c compiles."""
    check50.c.compile("find.c", lcs50=True)

@check50.check(compiles)
def finds_42_in_50():
    """finds 42 in 50 sorted numbers"""
    check50.run("./find 42 -s 50").stdout("Found needle in haystack")

@check50.check(compiles)
def finds_28_in_100():
    """finds 28 in 100 sorted numbers"""
    check50.run("./find 28 -s 100").stdout("Found needle in haystack")

@check50.check(compiles)
def not_find_42_in_30():
    """does not find 42 in 30 sorted numbers"""
    check50.run("./find 42 -s 30").stdout("Didn't find needle in haystack")

def finds_0_in_1():
    """finds 0 in 1 sorted number"""
    check50.run("./find 0 -s 1").stdout("Found needle in haystack")