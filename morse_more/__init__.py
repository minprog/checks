import check50
import check50.c
import base64

@check50.check()
def exists():
    """morse_more.c exists"""
    check50.exists("morse_more.c")

@check50.check(exists)
def compiles():
    """morse_more.c compiles"""
    check50.c.compile("morse_more.c", lcs50=True)

@check50.check(compiles)
def test_hello_world():
    """=,=,=,=,,,=,,,=,===,=,=,,,=,===,=,=,,,===,===,===,,,,,,,=,===,===,,,===,===,===,,,=,===,=,,,=,===,=,=,,,===,=,="""
    (check50
        .run("./morse_more =,=,=,=,,,=,,,=,===,=,=,,,=,===,=,=,,,===,===,===,,,,,,,=,===,===,,,===,===,===,,,=,===,=,,,=,===,=,=,,,===,=,=")
        .stdout("hello world"))

@check50.check(test_hello_world)
def test_morse_code():
    """===,===,,,===,===,===,,,=,===,=,,,=,=,=,,,=,,,,,,,===,=,===,=,,,===,===,===,,,===,=,=,,,="""
    (check50
        .run("./morse_more ===,===,,,===,===,===,,,=,===,=,,,=,=,=,,,=,,,,,,,===,=,===,=,,,===,===,===,,,===,=,=,,,=")
        .stdout("morse code"))

@check50.check(test_morse_code)
def test_secret():
    """=,=,=,=,,,=,,,===,,,,,,,===,===,=,,,=,,,=,=,=,=,,,=,,,=,=,,,===,===,,,,,,,=,=,,,=,=,=,,,,,,,=,=,=,,,===,=,,,=,===,,,===,=,===,=,,,===,=,==="""
    out = (check50
        .run("./morse_more =,=,=,=,,,=,,,===,,,,,,,===,===,=,,,=,,,=,=,=,=,,,=,,,=,=,,,===,===,,,,,,,=,=,,,=,=,=,,,,,,,=,=,=,,,===,=,,,=,===,,,===,=,===,=,,,===,=,===")
        .stdout())
    
    out = base64.b64encode(str.encode(out.strip()))

    if b'aGV0IGdlaGVpbSBpcyBzbmFjaw==' not in out:
        raise check50.Failure("")

    check50.log("zeg dit tegen Jelle of Martijn")