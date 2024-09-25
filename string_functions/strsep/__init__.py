import check50
import check50.c
import check50.internal
import re

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../../helpers/helpers.py"
)
helpers.set_stdout_limit(10000)


@check50.check()
def exists():
    """strsep.c exists"""
    check50.exists("strsep.c")


@check50.check(exists)
def no_malloc():
    """malloc() is not used for strsep"""
    with open("strsep.c") as f:
        content = f.read()

        for i, line in enumerate(content.split("\n")):
            if "malloc" in line:
                line_nr = i + 1
                raise check50.Failure(f"found malloc on line {line_nr}: {line}")


@check50.check(exists)
def hello_world():
    '''strsep_ with "Hello+World" and "+" as seperator returns "World"'''
    main = r"""
int main(void)
{
    char string_arr[] = "Hello+World";
    char* str = string_arr;
    printf("original: %p\n", str);
    char* out = strsep(&str, "+");
    printf("new: %p\n", out);
    printf("stringp: %p\n", str);
    printf("token: %s\n", out);
    printf("string: %s\n", str);
}
"""

    with helpers.replace_main("strsep.c", main):
        check50.c.compile("strsep.c")
        out = check50.run("./strsep").stdout()
        original = re.search(r"original: (.*)\n", out).group(1)
        new = re.search(r"new: (.*)\n", out).group(1)
        stringp = re.search(r"stringp: (.*)\n", out).group(1)
        token = re.search(r"token: (.*)\n", out).group(1)
        string = re.search(r"string: (.*)\n", out).group(1)

        if int(original, base=16) != int(new, base=16):
            raise check50.Failure(f"expected strsep to return the original string {original}, but found {new}")

        if int(stringp, base=16) - int(original, base=16) != 6:
            raise check50.Failure(f"expected strsep to modifiy *stringp to {original} + 6, but found {stringp}")

        if string != "World":
            raise check50.Failure(f'expected stringp to be "World", but found {string}')
        
        if token != "Hello":
            raise check50.Failure(f'expected the returned token to be "Hello", but found {token}')
        