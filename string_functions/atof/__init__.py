import check50
import check50.c
import check50.internal
import re

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../../helpers/helpers.py"
)
helpers.set_stdout_limit(10000)


def find_last_include_line(content):
    last_include_line = None
    
    for line_number, line in enumerate(content.split("\n")):
        if '#include' in line:
            last_include_line = line_number

    return last_include_line


def inject_malloc_macro(filename):
    with open(filename, "r") as f:
        content = f.read()

    with open(filename, "w") as f:
        last_include_line = find_last_include_line(content)
        lines = content.split("\n")
        lines = lines[:last_include_line + 1] + [r'#define malloc(x) malloc(x); printf("%lu\n", x)'] + lines[last_include_line + 1:]
        content = "\n".join(lines)
        f.write(content)


@check50.check()
def exists():
    """atof.c exists"""
    check50.exists("atof.c")

@check50.check(exists)
def atof_12345():
    '''atof_("12.345") returns 12.345'''
    check_atof("12.345", 3)

@check50.check(exists)
def atof_0():
    '''atof_("0") returns 0.0'''
    check_atof("0", 1)

@check50.check(exists)
def atof_minus_2():
    '''atof_("-2") returns -2.0'''
    check_atof("-2", 1)

@check50.check(exists)
def atof_minus_11():
    '''atof_("-1.1") returns -1.1'''
    check_atof("-1.1", 1)

@check50.check(exists)
def ftoa_1234():
    '''ftoa_(12.34, 2) returns "12.34"'''
    check_ftoa("12.34", 2)

@check50.check(exists)
def ftoa_0_10():
    '''ftoa_(0, 10) returns "0.0"'''
    check_ftoa("0", 10)

@check50.check(exists)
def ftoa_2812_6():
    '''ftoa_(28.12, 6) returns "28.12"'''
    check_ftoa("28.12", 6)

@check50.check(exists)
def ftoa_2_4():
    '''ftoa_(2, 4) returns "2.0"'''
    check_ftoa("2", 4)

@check50.check(exists)
def ftoa_30_3():
    '''ftoa_(3.0, 3) returns "3.0"'''
    check_ftoa("3.0", 3)

@check50.check(exists)
def ftoa_0_3():
    '''ftoa_(0, 3) returns "0.0"'''
    check_ftoa("0", 3)

def check_atof(arg: str, precision: int) -> None:
    main = r"""
int main(void)
{
    float n = atof_("<placeholder1>");
    printf("%.<placeholder2>f", n);
}
"""
    main = main.replace("<placeholder1>", arg)
    main = main.replace("<placeholder2>", str(precision))

    with helpers.replace_main("atof.c", main):
        check50.c.compile("atof.c")
        out = check50.run("./atof").stdout()

        arg = str(float(arg))
        if out != arg:
            raise check50.Failure(f"expected {arg} but found {out}")


def check_ftoa(arg: str, precision: int) -> None:
    main = r"""
int main(void)
{
    char* str = ftoa_(<placeholder1>, <placeholder2>);
    printf("%s", str);
}
"""
    main = main.replace("<placeholder1>", arg)
    main = main.replace("<placeholder2>", str(precision))
    
    with helpers.replace_main("atof.c", main):
        check50.c.compile("atof.c")
        out = check50.run("./atof").stdout()

        arg = str(float(arg))
        if out != arg:
            raise check50.Failure(f"expected {arg} but found {out}")
    
    # TODO: check for alloc with both malloc and/or realloc?