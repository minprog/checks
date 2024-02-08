import check50
import check50.c
import check50.internal

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)

@check50.check()
def exists():
    """regen.c exists"""
    check50.exists("regen.c")

@check50.check(exists)
def compiles():
    """regen.c compiles"""
    check50.c.compile("regen.c", lcs50=True)

@check50.check(compiles)
def test_regen_12():
    """regen met 12, 12, 999 print 12 gemiddeld"""
    (check50.run("./regen")
        .stdin("12")
        .stdin("12")
        .stdin("999")
        .stdout("[Gg]emiddeld 12(?!\d)", str_output="Gemiddeld 12 millimeter"))

@check50.check(compiles)
def test_regen_7():
    """regen met 12, 6, 3, 999 print 7 gemiddeld"""
    (check50.run("./regen")
        .stdin("12")
        .stdin("6")
        .stdin("3")
        .stdin("999")
        .stdout("[Gg]emiddeld 7(?!\d)", str_output="Gemiddeld 7 millimeter"))

@check50.check(compiles)
def test_regen_11():
    """regen met 12, 11, 999 print 11 gemiddeld"""
    (check50.run("./regen")
        .stdin("12")
        .stdin("11")
        .stdin("999")
        .stdout("[Gg]emiddeld 11(?!\d)", str_output="Gemiddeld 11 millimeter"))

@check50.check(compiles)
def test_regen_invalid():
    """regen met 999 print Dat kan niet"""
    (check50.run("./regen")
        .stdin("999")
        .stdout("[Dd][ai]t kan niet", str_output="Dat kan niet"))
