import check50
import check50.c
import check50.internal

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)
helpers.set_stdout_limit(10000)


@check50.check()
def exists():
    """calculator.c exists"""
    check50.exists("calculator.c")

@check50.check(exists)
def compiles():
    """calculator.c compiles"""
    check50.c.compile("calculator.c", lcs50=True)

@check50.check(compiles)
def supports_all_ops():
    """calculator kan herhaaldelijk rekenen met +, -, * en / (0 + 1 - 3 * 4 + 16 / 4)"""
    (check50.run("./calculator")
        .stdin("0", prompt=False)
        .stdin("+", prompt=False)
        .stdin("1", prompt=False)
        .stdout("= 1")
        .stdin("-", prompt=False)
        .stdin("3", prompt=False)
        .stdout("= -2")
        .stdin("*", prompt=False)
        .stdin("4", prompt=False)
        .stdout("= -8")
        .stdin("+", prompt=False)
        .stdin("16", prompt=False)
        .stdout("= 8")
        .stdin("/", prompt=False)
        .stdin("4", prompt=False)
        .stdout("2")
    )

@check50.check(compiles)
def wrong_ops():
    """calculator negeert verkeerde operaties (2 $ % + 1)"""
    (check50.run("./calculator")
        .stdin("2", prompt=False)
        .stdin("$", prompt=False)
        .stdin("%", prompt=False)
        .stdin("+", prompt=False)
        .stdin("1", prompt=False)
        .stdout("= 3")
    )

@check50.check(compiles)
def handles_negatives():
    """calculator kan omgaan met negatieve getallen (-4 + -5 * -2)"""
    (check50.run("./calculator")
        .stdin("-4", prompt=False)
        .stdin("+", prompt=False)
        .stdin("-5", prompt=False)
        .stdout("= -9")
        .stdin("*", prompt=False)
        .stdin("-2", prompt=False)
        .stdout("= 18")
    )

@check50.check(compiles)
def round_division_down():
    """calculator rond naar beneden af (1 / 2)"""
    (check50.run("./calculator")
        .stdin("1", prompt=False)
        .stdin("/", prompt=False)
        .stdin("2", prompt=False)
        .stdout("= 0")
    )