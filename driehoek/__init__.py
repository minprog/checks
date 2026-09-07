import check50
import check50.c

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)
helpers.set_stdout_limit(10000)


DRIEHOEK5 = """\
    ##
   #  #
  #    #
 #      #
##########"""

DRIEHOEK20 = """\
                   ##
                  #  #
                 #    #
                #      #
               #        #
              #          #
             #            #
            #              #
           #                #
          #                  #
         #                    #
        #                      #
       #                        #
      #                          #
     #                            #
    #                              #
   #                                #
  #                                  #
 #                                    #
########################################"""


def check_driehoek(stdins, driehoek):
    """Run ./driehoek with stdins and expect driehoek as its output."""
    process = check50.run("./driehoek")

    for line in stdins:
        process.stdin(line)

    return helpers.expect_ascii_art(process, driehoek)


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
    check_driehoek(["5"], DRIEHOEK5).exit(0)


@check50.check(test_driehoek5)
def test_driehoek20():
    """driehoek met hoogte 20 is correct"""
    check_driehoek(["20"], DRIEHOEK20).exit(0)
