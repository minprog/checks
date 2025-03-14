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
    """atoi.c exists"""
    check50.exists("atoi.c")

@check50.check(exists)
def atoi_1234():
    '''atoi_("1234") returns 1234'''
    check_atoi("1234")

@check50.check(exists)
def atoi_0():
    '''atoi_("0") returns 0'''
    check_atoi("0")

@check50.check(exists)
def atoi_minus_1():
    '''atoi_("-1") returns -1'''
    check_atoi("-1")

@check50.check(exists)
def itoa_1234():
    '''itoa_(1234) returns "1234"'''
    check_itoa("1234")

@check50.check(exists)
def itoa_0():
    '''itoa_(0) returns "0"'''
    check_itoa("0")


@check50.check(exists)
def itoa_minus_1():
    '''itoa_(-1) returns "-1"'''
    check_itoa("-1")

def check_atoi(arg: str) -> None:
    main = r"""
int main(void)
{
    int n = atoi_("<placeholder>");
    printf("%d", n);
}
"""
    main = main.replace("<placeholder>", arg)

    with helpers.replace_main("atoi.c", main):
        check50.c.compile("atoi.c")
        out = check50.run("./atoi").stdout()

        if out != arg:
            raise check50.Failure(f"expected {arg} but found {out}")


def check_itoa(arg: str) -> None:
    main = r"""
int main(void)
{
    char* str = itoa_(<placeholder>);
    printf("%s", str);
}
"""
    main = main.replace("<placeholder>", arg)
    
    with helpers.replace_main("atoi.c", main):
        check50.c.compile("atoi.c")
        out = check50.run("./atoi").stdout()

        if out != arg:
            raise check50.Failure(f"expected {arg} but found {out}")

    main = r"""
int main(void)
{
    itoa_(<placeholder>);
}
"""
    main = main.replace("<placeholder>", arg)

    with helpers.replace_main("atoi.c", main):
        inject_malloc_macro("atoi.c")
        check50.c.compile("atoi.c")
        out = check50.run("./atoi").stdout()

        numbers = re.findall(r'\d+', out)
        malloc_byte_count = len(arg) + 1
        if str(malloc_byte_count) not in numbers:
            if not numbers:
                raise check50.Failure(f"expected itoa_ to malloc exactly {malloc_byte_count} bytes, but the code malloc'd no byte(s)")
            raise check50.Failure(f"expected itoa_ to malloc exactly {malloc_byte_count} bytes, but the code malloc'd {numbers[0]} byte(s)")
