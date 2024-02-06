import check50
import check50.c

@check50.check()
def exists():
    """cirkel.c exists"""
    check50.exists("cirkel.c")

@check50.check(exists)
def compiles():
    """cirkel.c compiles"""
    check50.c.compile("cirkel.c", lcs50=True)

@check50.check(compiles)
def test_cirkel5():
    """cirkel met hoogte 5 is correct"""
    answer = (
        "   xxxxx\s*\n"   
        "  x     x\s*\n"  
        " x       x\s*\n" 
        "x         x\s*\n"
        "x         x\s*\n"
        "x         x\s*\n"
        "x         x\s*\n"
        "x         x\s*\n"
        " x       x\s*\n" 
        "  x     x\s*\n"  
        "   xxxxx\s*\n" 
    )
    readable_answer = answer.replace("\s*", "")
    check50.run("./cirkel").stdin("5").stdout(answer, str_output=readable_answer).exit(0)

@check50.check(compiles)
def test_cirkel10():
    """cirkel met hoogte 10 is correct"""
    answer = (
        "       xxxxxxx\s*\n"
        "     xx       xx\s*\n"
        "    x           x\s*\n"
        "   x             x\s*\n"   
        "  x               x\s*\n"  
        " x                 x\s*\n" 
        " x                 x\s*\n" 
        "x                   x\s*\n"
        "x                   x\s*\n"
        "x                   x\s*\n"
        "x                   x\s*\n"
        "x                   x\s*\n"
        "x                   x\s*\n"
        "x                   x\s*\n"
        " x                 x\s*\n" 
        " x                 x\s*\n" 
        "  x               x\s*\n"  
        "   x             x\s*\n"   
        "    x           x\s*\n"    
        "     xx       xx\s*\n"     
        "       xxxxxxx\s*\n"
    )
    readable_answer = answer.replace(r"\s*", "")
    check50.run("./cirkel").stdin("10").stdout(answer, str_output=readable_answer).exit(0)

@check50.check(compiles)
def test_cirkel_incorrect_input():
    """vraagt opnieuw om input bij een incorrecte hoogte van 3"""
    answer = (
        "   xxxxx\s*\n"   
        "  x     x\s*\n"  
        " x       x\s*\n" 
        "x         x\s*\n"
        "x         x\s*\n"
        "x         x\s*\n"
        "x         x\s*\n"
        "x         x\s*\n"
        " x       x\s*\n" 
        "  x     x\s*\n"  
        "   xxxxx\s*\n" 
    )
    readable_answer = answer.replace("\s*", "")
    check50.run("./cirkel").stdin("3").stdin("5").stdout(answer, str_output=readable_answer).exit(0)
