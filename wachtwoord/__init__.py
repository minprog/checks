import check50
import check50.c

@check50.check()
def exists():
    """wachtwoord.c exists"""
    check50.exists("wachtwoord.c")

@check50.check(exists)
def compiles():
    """wachtwoord.c compiles"""
    check50.c.compile("wachtwoord.c", lcs50=True)

@check50.check(compiles)
def test_sterk_genoeg():
    """invoer van "mamamama" print "Sterk genoeg!\""""
    (check50.run("./wachtwoord")
        .stdin("mamamama")
        .stdout(r"[Ss]terk genoeg\!", str_output="Sterk genoeg!")
        .exit(0))

@check50.check(compiles)
def test_1_keer_niet_sterk():
    """invoer van "geheim" print "Niet sterk genoeg!", vervolgens invoer van "kruipluik" print "Sterk genoeg!\""""
    (check50.run("./wachtwoord")
        .stdin("geheim")
        .stdout(r"[Nn]iet sterk genoeg\!", str_output="Niet sterk genoeg!")
        .stdin("kruipluik")
        .stdout(r"[Ss]terk genoeg\!", str_output="Sterk genoeg!")
        .exit(0))

@check50.check(compiles)
def test_3_keer_niet_sterk():
    """invoer van drie zwakke wachtwoorden en vervolgens één sterk wachtwoord print de juiste uitvoer"""
    (check50.run("./wachtwoord")
        .stdin("geheim")
        .stdout(r"[Nn]iet sterk genoeg\!", str_output="Niet sterk genoeg!")
        .stdin("aardbei121")
        .stdout(r"[Nn]iet sterk genoeg\!", str_output="Niet sterk genoeg!")
        .stdin("roomboter")
        .stdout(r"[Nn]iet sterk genoeg\!", str_output="Niet sterk genoeg!")
        .stdin("kruipluik")
        .stdout(r"[Ss]terk genoeg\!", str_output="Sterk genoeg!")
        .exit(0))

@check50.check(compiles)
def test_20_keer_niet_sterk():
    """invoer van twintig zwakke wachtwoorden en vervolgens één sterk wachtwoord print de juiste uitvoer (aardbei121, tekort1, teveellettersachterelkaar, a)"""
    check = check50.run("./wachtwoord")

    for ww in ["aardbei121", "tekort1", "teveellettersachterelkaar", "a"] * 5:
        check = check.stdin(ww).stdout(r"[Nn]iet sterk genoeg\!", str_output="Niet sterk genoeg!")
        
    (check.stdin("goedgenoeg1")
        .stdout(r"[Ss]terk genoeg\!", str_output="Sterk genoeg!")
        .exit(0))