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
    """strrchr.c exists"""
    check50.exists("strrchr.c")


@check50.check(exists)
def no_malloc():
    """malloc() is not used for strrchr"""
    with open("strrchr.c") as f:
        content = f.read()

        for i, line in enumerate(content.split("\n")):
            if "malloc" in line:
                line_nr = i + 1
                raise check50.Failure(f"found malloc on line {line_nr}: {line}")


@check50.check(exists)
def find_middle_char():
    '''strrchr_("abcd", 'c') returns "cd"'''
    main = r"""
int main(void)
{
    printf("%s", strrchr_("abcd", 'c'));
}
"""

    with helpers.replace_main("strrchr.c", main):
        check50.c.compile("strrchr.c")
        out = check50.run("./strrchr").stdout()
        expected = "cd"
        if out != expected:
            raise check50.Failure(f"expected {expected} but found {out}")
        

@check50.check(exists)
def find_first_char():
    '''strrchr_("abcd", 'a') returns "abcd"'''
    main = r"""
int main(void)
{
    printf("%s", strrchr_("abcd", 'a'));
}
"""

    with helpers.replace_main("strrchr.c", main):
        check50.c.compile("strrchr.c")
        out = check50.run("./strrchr").stdout()
        expected = "abcd"
        if out != expected:
            raise check50.Failure(f"expected {expected} but found {out}")


@check50.check(exists)
def find_last_char():
    '''strrchr_("abcd", 'd') returns "d"'''
    main = r"""
int main(void)
{
    printf("%s", strrchr_("abcd", 'd'));
}
"""

    with helpers.replace_main("strrchr.c", main):
        check50.c.compile("strrchr.c")
        out = check50.run("./strrchr").stdout()
        expected = "d"
        if out != expected:
            raise check50.Failure(f"expected {expected} but found {out}")


@check50.check(exists)
def find_missing_char():
    '''strrchr_("abcd", 'e') returns NULL'''
    main = r"""
int main(void)
{
    if (strrchr_("abcd", 'e') == NULL)
    {
        printf("NULL");
    }
    else
    {
        printf("%s", strrchr_("abcd", 'e'));
    }
}
"""

    with helpers.replace_main("strrchr.c", main):
        check50.c.compile("strrchr.c")
        out = check50.run("./strrchr").stdout()
        expected = "NULL"
        if out != expected:
            raise check50.Failure(f"expected {expected} but found {out}")


@check50.check(exists)
def find_last_char_in_duplicate():
    '''strrchr_("abba", 'b') returns "ba"'''
    main = r"""
int main(void)
{
    printf("%s", strrchr_("abba", 'b'));
}
"""

    with helpers.replace_main("strrchr.c", main):
        check50.c.compile("strrchr.c")
        out = check50.run("./strrchr").stdout()
        expected = "ba"
        if out != expected:
            raise check50.Failure(f"expected {expected} but found {out}")


@check50.check(exists)
def find_term_char():
    '''strrchr_("abcd", '\\0') returns ""'''
    main = r"""
int main(void)
{
    if (strrchr_("abcd", '\0') == NULL)
    {
        printf("NULL");
    }
    else if (strcmp(strrchr_("abcd", '\0'), "") == 0)
    {
        printf("great success");
    }
    else
    {
        printf("%s", strrchr_("abcd", '\0'));
    }
}
"""

    with helpers.replace_main("strrchr.c", main):
        check50.c.compile("strrchr.c")
        out = check50.run("./strrchr").stdout()
        expected = "great success"
        if out != expected:
            raise check50.Failure(f"expected \"\" but found {out}")

