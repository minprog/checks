import check50
import check50.c

@check50.check()
def exists():
    """formule.c exists"""
    check50.exists("formule.c")

@check50.check(exists)
def compiles():
    """formule.c compiles"""
    check50.c.compile("formule.c", lcs50=True)

@check50.check(compiles)
def test_hello_world():
    """hello world! print Er zijn geen fouten."""
    (check50.run("./formule")
        .stdin("hello world!")
        .stdout("[Ee]r zijn geen fouten\.", str_output="Er zijn geen fouten.")
        .exit(0))

@check50.check(compiles)
def test_genoeg():
    """(a + b - (c * d)) print Er zijn geen fouten."""
    (check50.run("./formule")
        .stdin("(a + b - (c * d))")
        .stdout("[Ee]r zijn geen fouten\.", str_output="Er zijn geen fouten.")
        .exit(0))
    
@check50.check(compiles)
def test_te_vroeg():
    """)a + b( print Er wordt een haakje te vroeg gesloten."""
    (check50.run("./formule")
        .stdin(")a + b(")
        .stdout("[Ee]r wordt een haakje te vroeg gesloten\.", str_output="Er wordt een haakje te vroeg gesloten.")
        .exit(0))

@check50.check(compiles)
def test_te_weinig():
    """a + (c * d print Er worden te weinig haakjes gesloten."""
    (check50.run("./formule")
        .stdin("a + (c * d")
        .stdout("[Ee]r worden te weinig haakjes gesloten\.", str_output="Er worden te weinig haakjes gesloten.")
        .exit(0))
