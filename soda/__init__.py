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
def starts_with_owed():
    """starts by printing how much is owed"""
    check50.run("./soda").stdout("50 cents owed")
    
@check50.check(compiles)
def two_coins():
    """accepts two 25 cents coins then prints 0 owed"""
    (check50.run("./soda")
        .stdout("50 cents owed")
        .stdin("25")
        .stdout("25 cents owed")
        .stdin("25")
        .stdout("0 cents change"))
    
@check50.check(compiles)
def handles_wrong_coin():
    """ignores invalid coins"""
    (check50.run("./soda")
        .stdout("50 cents owed")
        .stdin("15")
        .stdout("50 cents owed")
        .stdin("3")
        .stdout("50 cents owed")
        .stdin("25")
        .stdout("25 cents owed")
        .stdin("30")
        .stdout("25 cents owed")
        .stdin("25")
        .stdout("0 cents change"))
    
@check50.check(compiles)
def gives_back_change():
    """gives back change"""
    (check50.run("./soda")
        .stdout("50 cents owed")
        .stdin("25")
        .stdout("25 cents owed")
        .stdin("10")
        .stdout("15 cents owed")
        .stdin("5")
        .stdout("10 cents owed")
        .stdin("25")
        .stdout("15 cents change"))