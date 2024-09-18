import check50
import check50.c
import check50.internal

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../../helpers/helpers.py"
)
helpers.set_stdout_limit(10000)


@check50.check()
def exists():
    """strcat.c exists"""
    check50.exists("strcat.c")


@check50.check(exists)
def cat_hello_world():
    '''strcat_("Hello", ' World') returns "Hello World"'''
    main = r"""
int main(void)
{
    char buffer[50] = "Hello";
    string cat_str = " World";
    string result = strcat_(buffer, cat_str);
    printf("%s", result);
}
"""

    with helpers.replace_main("strcat.c", main):
        check50.c.compile("strcat.c")
        out = check50.run("./strcat").stdout()
        expected = "Hello World"
        if out != expected:
            raise check50.Failure(f"expected {expected} but found {out}")
        

@check50.check(exists)
def cat_hello_world_in_place():
    '''strcat_("Hello", ' World') modifies "Hello" to "Hello World"'''
    main = r"""
int main(void)
{
    char buffer[50] = "Hello";
    string cat_str = " World";
    strcat_(buffer, cat_str);
    printf("%s", buffer);
}
"""

    with helpers.replace_main("strcat.c", main):
        check50.c.compile("strcat.c")
        out = check50.run("./strcat").stdout()
        expected = "Hello World"
        if out != expected:
            raise check50.Failure(f"expected {expected} but found {out}")
