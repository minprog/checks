import check50
import check50.c

@check50.check()
def exists():
    """soda.c exists"""
    check50.exists("soda.c")

@check50.check(exists)
def compiles():
    """soda.c compiles"""
    check50.c.compile("soda.c", lcs50=True)

@check50.check(compiles)
def starts_with_cents_owed():
    check50.run("./soda").stdout("50 cents owed")