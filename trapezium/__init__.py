import check50
import check50.c

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)
helpers.set_stdout_limit(10000)


TRAPEZIUM5 = """\
    ##########
   #        #
  #        #
 #        #
##########"""

TRAPEZIUM15 = """\
              ##############################
             #                            #
            #                            #
           #                            #
          #                            #
         #                            #
        #                            #
       #                            #
      #                            #
     #                            #
    #                            #
   #                            #
  #                            #
 #                            #
##############################"""


def check_trapezium(stdins, trapezium):
    """Run ./trapezium with stdins and expect trapezium as its output."""
    process = check50.run("./trapezium")

    for line in stdins:
        process.stdin(line)

    return helpers.expect_ascii_art(process, trapezium)


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
    check_trapezium(["5"], TRAPEZIUM5).exit(0)


@check50.check(compiles)
def test_trapezium20():
    """trapezium met hoogte 15 is correct"""
    check_trapezium(["15"], TRAPEZIUM15).exit(0)


@check50.check(compiles)
def test_trapezium_invalid_input():
    """trapezium vraagt opnieuw bij foute input"""
    check_trapezium(["-3", "40", "3", "5"], TRAPEZIUM5)
