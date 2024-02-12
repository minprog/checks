import check50
import check50.c

@check50.check()
def exists():
    """tennis.c exists"""
    check50.exists("tennis.c")

@check50.check(exists)
def compiles():
    """tennis.c compiles"""
    check50.c.compile("tennis.c", lcs50=True)

@check50.check(compiles)
def test_tennis_instant_lose():
    """tennis met de woorden "hello" "world" doet speler 1 winnen"""
    (check50.run("./tennis")
        .stdin("hello")
        .stdin("world")
        .stdout("[Ss]peler 1 wint", str_output="Speler 1 wint!")
        .exit(0))

@check50.check(compiles)
def test_tennis_five_guesses():
    """tennis met de woorden "dat" "tentamen" "nooit" "top" "wijk" doet speler 2 winnen"""
    (check50.run("./tennis")
        .stdin("dat")
        .stdin("tentamen")
        .stdin("nooit")
        .stdin("top")
        .stdin("wijk")
        .stdout("[Ss]peler 2 wint", str_output="Speler 2 wint!")
        .exit(0))

@check50.check(compiles)
def test_tennis_four_guesses():
    """tennis met de woorden "dit" "top" "parfum" "uitzonderlijk" doet speler 1 winnen"""
    (check50.run("./tennis")
        .stdin("dit")
        .stdin("top")
        .stdin("parfum")
        .stdin("uitzonderlijk")
        .stdout("[Ss]peler 1 wint", str_output="Speler 1 wint!")
        .exit(0))

