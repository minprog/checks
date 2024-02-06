import check50
import check50.c
import check50.internal

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)

@check50.check()
def exists():
    """driehoek.c exists"""
    check50.exists("driehoek.c")

@check50.check(exists)
def compiles():
    """driehoek.c compiles"""
    check50.c.compile("driehoek.c", lcs50=True)

@check50.check(compiles)
def test_driehoek5():
    """driehoek met hoogte 5 is correct"""
    answer = (
        "    ##(\s)*\n"
        "   #  #(\s)*\n"
        "  #    #(\s)*\n"
        " #      #(\s)*\n"
        "##########(\s)*\n"
    )
    readable_answer = answer.replace("(\s)*", "")
    check50.run("./driehoek").stdin("5").stdout(answer, str_output=readable_answer).exit(0)

@check50.check(compiles)
def test_driehoek20():
    """driehoek met hoogte 20 is correct"""
    answer = (
        "                   ##(\s)*\n"
        "                  #  #(\s)*\n"
        "                 #    #(\s)*\n"
        "                #      #(\s)*\n"
        "               #        #(\s)*\n"
        "              #          #(\s)*\n"
        "             #            #(\s)*\n"
        "            #              #(\s)*\n"
        "           #                #(\s)*\n"
        "          #                  #(\s)*\n"
        "         #                    #(\s)*\n"
        "        #                      #(\s)*\n"
        "       #                        #(\s)*\n"
        "      #                          #(\s)*\n"
        "     #                            #(\s)*\n"
        "    #                              #(\s)*\n"
        "   #                                #(\s)*\n"
        "  #                                  #(\s)*\n"
        " #                                    #(\s)*\n"
        "########################################(\s)*\n"
    )
    readable_answer = answer.replace("(\s)*", "")
    check50.run("./driehoek").stdin("20").stdout(answer, str_output=readable_answer).exit(0)