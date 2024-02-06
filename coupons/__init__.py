import check50
import check50.c
import check50.internal

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)

@check50.check()
def exists():
    """coupons.c exists"""
    check50.exists("coupons.c")

@check50.check(exists)
def compiles():
    """coupons.c compiles"""
    check50.c.compile("coupons.c", lcs50=True)

@check50.check(compiles)
def has_functions():
    """coupons.c has the functions: bereken_coupon1, bereken_coupon2, bereken_coupon3"""
    with open("coupons.c") as f:
        content = f.read()

    for name in ["bereken_coupon1", "bereken_coupon2", "bereken_coupon3"]:
        if f" {name}(" not in content:
            raise check50.Failure(f"Missing function: {name}")

@check50.check(has_functions)
def test_coupon1_exact():
    """bereken_coupon1(3, 5.90) returns 11.80"""
    main = (
        'int main(void) {\n'
        '    printf("%.2f", bereken_coupon1(3, 5.90));\n'
        '}'
    )

    with helpers.replace_main("coupons.c", main):
        check50.c.compile("coupons.c", lcs50=True)
        check50.run("./coupons").stdout("11.80").exit(0)

@check50.check(has_functions)
def test_coupon1_off():
    """bereken_coupon1(4, 4.0) returns 12.0"""
    main = (
        'int main(void) {\n'
        '    printf("%.2f", bereken_coupon1(4, 4.0));\n'
        '}'
    )

    with helpers.replace_main("coupons.c", main):
        check50.c.compile("coupons.c", lcs50=True)
        check50.run("./coupons").stdout("12.0").exit(0)

@check50.check(has_functions)
def test_coupon2_exact():
    """bereken_coupon2(2, 2.5) returns 3.75"""
    main = (
        'int main(void) {\n'
        '    printf("%.2f", bereken_coupon2(2, 2.5));\n'
        '}'
    )

    with helpers.replace_main("coupons.c", main):
        check50.c.compile("coupons.c", lcs50=True)
        check50.run("./coupons").stdout("3.75").exit(0)

@check50.check(has_functions)
def test_coupon2_off():
    """bereken_coupon2(5, 1.5) returns 6.0"""
    main = (
        'int main(void) {\n'
        '    printf("%.2f", bereken_coupon2(5, 1.5));\n'
        '}'
    )

    with helpers.replace_main("coupons.c", main):
        check50.c.compile("coupons.c", lcs50=True)
        check50.run("./coupons").stdout("6.0").exit(0)

@check50.check(has_functions)
def test_coupon3_exact2():
    """bereken_coupon3(2, 5.0) returns 9.0"""
    main = (
        'int main(void) {\n'
        '    printf("%.2f", bereken_coupon3(2, 5.0));\n'
        '}'
    )

    with helpers.replace_main("coupons.c", main):
        check50.c.compile("coupons.c", lcs50=True)
        check50.run("./coupons").stdout("9.0").exit(0)

@check50.check(has_functions)
def test_coupon3_exact4():
    """bereken_coupon3(4, 2.5) returns 7.0"""
    main = (
        'int main(void) {\n'
        '    printf("%.2f", bereken_coupon3(4, 2.5));\n'
        '}'
    )

    with helpers.replace_main("coupons.c", main):
        check50.c.compile("coupons.c", lcs50=True)
        check50.run("./coupons").stdout("7.0").exit(0)

@check50.check(has_functions)
def test_program_coupon2():
    """2 stuks kopen met een prijs van 5.90 geeft coupon 2 en een totale prijs van 8.85"""
    check50.run("./coupons").stdin("2").stdin("5.90").stdout("coupon 2").stdout("8.85").exit(0)

@check50.check(has_functions)
def test_program_coupon3():
    """1 stuk kopen met een prijs van 2.80 geeft coupon 3 en een totale prijs van 2.66"""
    check50.run("./coupons").stdin("1").stdin("2.80").stdout("coupon 3").stdout("2.66").exit(0)

@check50.check(has_functions)
def test_program_coupon1():
    """3 stuks kopen met een prijs van 3.10 geeft coupon 1 en een totale prijs van 6.20"""
    check50.run("./coupons").stdin("3").stdin("3.10").stdout("coupon 1").stdout("6.20").exit(0)