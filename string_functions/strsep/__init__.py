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
    char* out = strsep_(&str, "+");
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
    

@check50.check(exists)
def foo_bar_baz_qux():
    '''strsep_ with "Foo/Bar-Baz+Qux" and "-/" as seperator returns "Foo", then "Bar", then "Baz+Qux"'''
    main = r"""
int main(void)
{
    char string_arr[] = "Foo/Bar-Baz+Qux";
    char* str = string_arr;
    printf("original1: %p\n", str);
    char* out = strsep_(&str, "-/");
    printf("new1: %p\n", out);
    printf("stringp1: %p\n", str);
    printf("token1: %s\n", out);
    printf("string1: %s\n", str);

    printf("original2: %p\n", str);
    out = strsep_(&str, "-/");
    printf("new2: %p\n", out);
    printf("stringp2: %p\n", str);
    printf("token2: %s\n", out);
    printf("string2: %s\n", str);

    printf("original3: %p\n", str);
    out = strsep_(&str, "-/");
    printf("new3: %p\n", out);
    printf("stringp3: %p\n", str);
    printf("token3: %s\n", out);
}
"""

    with helpers.replace_main("strsep.c", main):
        check50.c.compile("strsep.c")
        out = check50.run("./strsep").stdout()
        original = re.search(r"original1: (.*)\n", out).group(1)
        new = re.search(r"new1: (.*)\n", out).group(1)
        stringp = re.search(r"stringp1: (.*)\n", out).group(1)
        token = re.search(r"token1: (.*)\n", out).group(1)
        string = re.search(r"string1: (.*)\n", out).group(1)

        if int(original, base=16) != int(new, base=16):
            raise check50.Failure(f"expected strsep to return the original string {original}, but found {new}")

        if int(stringp, base=16) - int(original, base=16) != 4:
            raise check50.Failure(f"expected strsep to modifiy *stringp to {original} + 4, but found {stringp}")

        if string != "Bar-Baz+Qux":
            raise check50.Failure(f'expected stringp to be "Bar-Baz+Qux", but found {string}')
        
        if token != "Foo":
            raise check50.Failure(f'expected the returned token to be "Foo", but found {token}')
        
        original = re.search(r"original2: (.*)\n", out).group(1)
        new = re.search(r"new2: (.*)\n", out).group(1)
        stringp = re.search(r"stringp2: (.*)\n", out).group(1)
        token = re.search(r"token2: (.*)\n", out).group(1)
        string = re.search(r"string2: (.*)\n", out).group(1)

        if int(original, base=16) != int(new, base=16):
            raise check50.Failure(f"expected strsep to return the original string {original}, but found {new}")

        if int(stringp, base=16) - int(original, base=16) != 4:
            raise check50.Failure(f"expected strsep to modifiy *stringp to {original} + 4, but found {stringp}")

        if string != "Baz+Qux":
            raise check50.Failure(f'expected stringp to be "Baz+Qux", but found {string}')
        
        if token != "Bar":
            raise check50.Failure(f'expected the returned token to be "Bar", but found {token}')
        
        original = re.search(r"original3: (.*)\n", out).group(1)
        new = re.search(r"new3: (.*)\n", out).group(1)
        stringp = re.search(r"stringp3: (.*)\n", out).group(1)
        token = re.search(r"token3: (.*)\n", out).group(1)
        
        if int(original, base=16) != int(new, base=16):
            raise check50.Failure(f"expected strsep to return the original string {original}, but found {new}")

        if int(stringp, base=16) != 0:
            raise check50.Failure(f"expected strsep to modifiy *stringp to NULL (0x0), but found {stringp}")

        if token != "Baz+Qux":
            raise check50.Failure(f'expected the returned token to be "Baz+Qux", but found {token}')


@check50.check(exists)
def null():
    '''strsep_ with NULL as *stringp and "hello world" as seperator returns NULL'''
    main = r"""
int main(void)
{
    char* str = NULL;
    printf("original1: %p\n", str);
    char* out = strsep_(&str, "hello world");
    printf("new1: %p\n", out);
    printf("stringp1: %p\n", str);
    printf("token_pointer1: %p\n", out);
    printf("token1: %s\n", out);
    printf("string1: %s\n", str);
}
"""

    with helpers.replace_main("strsep.c", main):
        check50.c.compile("strsep.c")
        out = check50.run("./strsep").stdout()
        original = re.search(r"original1: (.*)\n", out).group(1)
        new = re.search(r"new1: (.*)\n", out).group(1)
        stringp = re.search(r"stringp1: (.*)\n", out).group(1)
        token_pointer = re.search(r"token_pointer1: (.*)\n", out).group(1)

        if int(stringp, base=16) != 0:
            raise check50.Failure(f"expected strsep to leave *stringp as 0x0, but found {stringp}")

        if int(token_pointer, base=16) != 0:
            raise check50.Failure(f'expected the returned token to be NULL (0x0), but found {token_pointer}')
        