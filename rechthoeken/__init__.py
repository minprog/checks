import check50
import check50.c

@check50.check()
def exists():
    """rechthoeken.c exists"""
    check50.exists("rechthoeken.c")

@check50.check(exists)
def compiles():
    """rechthoeken.c compiles"""
    check50.c.compile("rechthoeken.c", lcs50=True)

@check50.check(compiles)
def test_example1():
    """rechthoeken met input 45, 33, 22, 12, V geeft 1221"""
    (check50.run("./rechthoeken")
        .stdin("45")
        .stdin("33")
        .stdin("22")
        .stdin("12")
        .stdin("V")
        .stdout("1221(?!\d)", str_output="1221"))

@check50.check(compiles)
def test_example2():
    """rechthoeken met input 1, 43, 39, 31, S geeft 1252"""
    (check50.run("./rechthoeken")
        .stdin("1")
        .stdin("43")
        .stdin("39")
        .stdin("31")
        .stdin("S")
        .stdout("1252(?!\d)", str_output="1252"))

@check50.check(compiles)
def test_example3():
    """rechthoeken met input 1, 43, 39, 31, 1 geeft 43"""
    (check50.run("./rechthoeken")
        .stdin("1")
        .stdin("43")
        .stdin("39")
        .stdin("31")
        .stdin("1")
        .stdout("43(?!\d)", str_output="43"))

@check50.check(compiles)
def test_example4():
    """rechthoeken met input 1, 43, 39, 31, X geeft: is geen geldige keuze"""
    (check50.run("./rechthoeken")
        .stdin("1")
        .stdin("43")
        .stdin("39")
        .stdin("31")
        .stdin("X")
        .stdout("is geen geldige keuze"))

@check50.check(compiles)
def test_example5():
    """rechthoeken met input 1, 43, 39, 31, 0 geeft: is geen geldige keuze"""
    (check50.run("./rechthoeken")
        .stdin("1")
        .stdin("43")
        .stdin("39")
        .stdin("31")
        .stdin("0")
        .stdout("is geen geldige keuze"))