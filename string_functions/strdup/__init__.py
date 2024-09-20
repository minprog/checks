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


def inject_malloc_macro():
    with open("strdup.c", "r") as f:
        content = f.read()

    with open("strdup.c", "w") as f:
        last_include_line = find_last_include_line(content)
        lines = content.split("\n")
        lines = lines[:last_include_line + 1] + [r'#define malloc(x) malloc(x); printf("%lu", x)'] + lines[last_include_line + 1:]
        content = "\n".join(lines)
        f.write(content)


@check50.check()
def exists():
    """strdup.c exists"""
    check50.exists("strdup.c")


@check50.check(exists)
def abcd():
    '''strdup_("abcd") returns "abcd"'''
    main = r"""
int main(void)
{
    printf("%s", strdup_("abcd"));
}
"""

    with helpers.replace_main("strdup.c", main):
        inject_malloc_macro()
        check50.c.compile("strdup.c")
        out = check50.run("./strdup").stdout()

        numbers = re.findall(r'\d+', out)
        if "5" not in numbers:
            raise check50.Failure(f"expected strdup to malloc exactly 5 bytes, but the code malloc'd {numbers[0]} byte(s)")

        out = re.sub(r'\d+', '', out)
        expected = "abcd"
        if expected != out:
            raise check50.Failure(f"expected {expected} but found {out}")
        

@check50.check(exists)
def empty():
    '''strdup_("") returns ""'''
    main = r"""
int main(void)
{
    printf("%s", strdup_(""));
}
"""

    with helpers.replace_main("strdup.c", main):
        inject_malloc_macro()
        check50.c.compile("strdup.c")
        out = check50.run("./strdup").stdout()

        numbers = re.findall(r'\d+', out)
        if "1" not in numbers:
            raise check50.Failure(f"expected strdup to malloc exactly 1 byte, but the code malloc'd {numbers[0]} byte(s)")

        out = re.sub(r'\d+', '', out)
        expected = ""
        if expected != out:
            raise check50.Failure(f"expected {expected} but found {out}")
        