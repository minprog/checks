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
def testUsage():
    """handles a missing command-line argument"""
    process = check50.run("./rna")
    out = process.stdout().strip()

    if out != "Usage: ./rna <DNA>":
        raise check50.Failure(f"expected Usage: ./rna <DNA>, but found {out}")

    check50.log("checking that program exited with status 1...")
    if process.exitcode != 1:
        raise check50.Failure(f"expected exit code 1, not {process.exitcode}")

@check50.check(compiles)
def testUsageTooManyArgs():
    """handles too many command-line arguments"""
    process = check50.run("./rna ATGC ATGC")
    out = process.stdout().strip()

    if out != "Usage: ./rna <DNA>":
        raise check50.Failure(f"expected Usage: ./rna <DNA>, but found {out}")

    check50.log("checking that program exited with status 1...")
    if process.exitcode != 1:
        raise check50.Failure(f"expected exit code 1, not {process.exitcode}")

@check50.check(compiles)
def testATGC():
    """transcribes ATGC as UACG"""
    (check50.run("./rna ATGC")
        .stdout("UACG", str_output="UACG"))

@check50.check(testATGC)
def testAAGGTTCCAA():
    """transcribes AAGGTTCCAA as UUCCAAGGUU"""
    (check50.run("./rna AAGGTTCCAA")
        .stdout("UUCCAAGGUU", str_output="UUCCAAGGUU"))

@check50.check(testAAGGTTCCAA)
def testCGaT():
    """transcribes CGaT as GCUA"""
    (check50.run("./rna CGaT")
        .stdout("GCUA", str_output="GCUA"))

@check50.check(testCGaT)
def testAAF():
    """handles invalid input (AAF)"""
    process = check50.run("./rna AAF")
    out = process.stdout().strip()

    if out != "Invalid DNA" and out != "invalid DNA":
        raise check50.Failure(f"expected Invalid DNA, but found {out}")

    check50.log("checking that program exited with status 1...")
    if process.exitcode != 1:
        raise check50.Failure(f"expected exit code 1, not {process.exitcode}")

@check50.check(testCGaT)
def testZATG():
    """handles invalid input (ZATG)"""
    process = check50.run("./rna ZATG")
    out = process.stdout().strip()

    if out != "Invalid DNA" and out != "invalid DNA":
        raise check50.Failure(f"expected Invalid DNA, but found {out}")

    check50.log("checking that program exited with status 1...")
    if process.exitcode != 1:
        raise check50.Failure(f"expected exit code 1, not {process.exitcode}")
