import check50
import check50.c

@check50.check()
def exists():
    """rna.c is correct"""
    check50.exists("rna.c")

@check50.check(exists)
def compiles():
    """rna.c compiles"""
    check50.c.compile("rna.c", "-lcs50")

@check50.check(compiles)
def testATGC():
    """transcribes ATGC as UACG"""
    (check50.run("./rna")
        .stdin("ATGC")
        .stdout("UACG", str_output="UACG"))

@check50.check(testATGC)
def testAAGGTTCCAA():
    """transcribes AAGGTTCCAA as UUCCAAGGUU"""
    (check50.run("./rna")
        .stdin("AAGGTTCCAA")
        .stdout("UUCCAAGGUU", str_output="UUCCAAGGUU"))

@check50.check(testAAGGTTCCAA)
def testCGaT():
    """transcribes CGaT as GCUA"""
    (check50.run("./rna")
        .stdin("CGaT")
        .stdout("GCUA", str_output="GCUA"))

@check50.check(testCGaT)
def testAAF():
    """handles invalid input (AAF)"""
    out = check50.run("./rna").stdin("AAF").stdout()
    out = out.strip()

    if out != "Invalid DNA" and out != "invalid DNA":
        raise check50.Failure(f"expected Invalid DNA, but found {out}")

@check50.check(testCGaT)
def testZATG():
    """handles invalid input (ZATG)"""
    out = check50.run("./rna").stdin("ZATG").stdout()
    out = out.strip()

    if out != "Invalid DNA" and out != "invalid DNA":
        raise check50.Failure(f"expected Invalid DNA, but found {out}")
