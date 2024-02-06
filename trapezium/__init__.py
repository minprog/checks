import check50
import check50.c

@check50.check()
def exists():
    """trapezium.c exists"""
    check50.exists("trapezium.c")

@check50.check(exists)
def compiles():
    """trapezium.c compiles"""
    check50.c.compile("trapezium.c", lcs50=True)

@check50.check(compiles)
def test_trapezium5():
    """trapezium met hoogte 5 is correct"""
    answer = (
        "    ##########(\s)*\n"
        "   #        #(\s)*\n"
        "  #        #(\s)*\n"
        " #        #(\s)*\n"
        "##########(\s)*"
    )
    readable_answer = answer.replace("(\s)*", "")
    check50.run("./trapezium").stdin("5").stdout(answer, str_output=readable_answer).exit(0)

@check50.check(compiles)
def test_trapezium20():
    """trapezium met hoogte 15 is correct"""
    answer = (
        "              ##############################(\s)*\n"
        "             #                            #(\s)*\n"
        "            #                            #(\s)*\n"
        "           #                            #(\s)*\n"
        "          #                            #(\s)*\n"
        "         #                            #(\s)*\n"
        "        #                            #(\s)*\n"
        "       #                            #(\s)*\n"
        "      #                            #(\s)*\n"
        "     #                            #(\s)*\n"
        "    #                            #(\s)*\n"
        "   #                            #(\s)*\n"
        "  #                            #(\s)*\n"
        " #                            #(\s)*\n"
        "##############################(\s)*"
    )
    readable_answer = answer.replace("(\s)*", "")
    check50.run("./trapezium").stdin("15").stdout(answer, str_output=readable_answer).exit(0)

@check50.check(compiles)
def test_trapezium_invalid_input():
    """trapezium vraagt opnieuw bij foute input"""
    answer = (
        "    ##########(\s)*\n"
        "   #        #(\s)*\n"
        "  #        #(\s)*\n"
        " #        #(\s)*\n"
        "##########(\s)*"
    )
    readable_answer = answer.replace("(\s)*", "")

    check = (check50.run("./trapezium")
        .stdin("-3")
        .stdin("40")
        .stdin("3")
        .stdin("5")
        .stdout(answer, str_output=readable_answer))
