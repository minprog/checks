import check50
import check50.c
import check50.internal

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)

@check50.check()
def exists():
    """repeat.c exists"""
    check50.exists("repeat.c")

@check50.check(exists)
def compiles():
    """repeat.c compiles"""
    check50.c.compile("repeat.c", lcs50=True)

@check50.check(compiles)
def test_repeat1():
    """repeat 1x "hello" prints hello"""
    check50.run("./repeat").stdin("hello").stdin("1").stdout("hello").exit(0)

@check50.check(compiles)
def test_repeat2():
    """repeat 2x "foo" prints foofoo"""
    check50.run("./repeat").stdin("foo").stdin("2").stdout("foo").exit(0)

@check50.check(compiles)
def test_repeat8():
    """repeat 8x "na" prints nananananananana"""
    check50.run("./repeat").stdin("na").stdin("8").stdout("nananananananana").exit(0)
