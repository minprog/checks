import check50
import check50.c

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)
helpers.set_stdout_limit(10000)

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
        r"   xxxxx\s*\n"   
        r"  x     x\s*\n"  
        r" x       x\s*\n" 
        r"x         x\s*\n"
        r"x         x\s*\n"
        r"x         x\s*\n"
        r"x         x\s*\n"
        r"x         x\s*\n"
        r" x       x\s*\n" 
        r"  x     x\s*\n"  
        r"   xxxxx\s*\n" 
    )
    readable_answer = answer.replace(r"\s*", "")
    check50.run("./cirkel").stdin("5").stdout(answer, str_output=readable_answer).exit(0)

@check50.check(compiles)
def test_cirkel10():
    """cirkel met hoogte 10 is correct"""
    answer = (
        r"       xxxxxxx\s*\n"
        r"     xx       xx\s*\n"
        r"    x           x\s*\n"
        r"   x             x\s*\n"   
        r"  x               x\s*\n"  
        r" x                 x\s*\n" 
        r" x                 x\s*\n" 
        r"x                   x\s*\n"
        r"x                   x\s*\n"
        r"x                   x\s*\n"
        r"x                   x\s*\n"
        r"x                   x\s*\n"
        r"x                   x\s*\n"
        r"x                   x\s*\n"
        r" x                 x\s*\n" 
        r" x                 x\s*\n" 
        r"  x               x\s*\n"  
        r"   x             x\s*\n"   
        r"    x           x\s*\n"    
        r"     xx       xx\s*\n"     
        r"       xxxxxxx\s*\n"
    )
    readable_answer = answer.replace(r"\s*", "")
    check50.run("./cirkel").stdin("10").stdout(answer, str_output=readable_answer).exit(0)

@check50.check(compiles)
def test_cirkel_incorrect_input():
    """vraagt opnieuw om input bij een incorrecte hoogte van 3"""
    answer = (
        r"   xxxxx\s*\n"   
        r"  x     x\s*\n"  
        r" x       x\s*\n" 
        r"x         x\s*\n"
        r"x         x\s*\n"
        r"x         x\s*\n"
        r"x         x\s*\n"
        r"x         x\s*\n"
        r" x       x\s*\n" 
        r"  x     x\s*\n"  
        r"   xxxxx\s*\n" 
    )
    readable_answer = answer.replace(r"\s*", "")
    check50.run("./cirkel").stdin("3").stdin("5").stdout(answer, str_output=readable_answer).exit(0)
