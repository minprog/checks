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
    """strchr.c exists"""
    check50.exists("strchr.c")


@check50.check(exists)
def compiles():
    """strchr.c compiles"""
    check50.c.compile("strchr.c", lcs50=True)


@check50.check(compiles)
def find_middle_char():
    '''strchr_("abcd", 'c') returns "cd"'''
    main = r"""
int main(void)
{
    printf("%s", strchr_("abcd", 'c'));
}
"""

    with helpers.replace_main("strchr.c", main):
        check50.c.compile("strchr.c")
        out = check50.run("./strchr").stdout()
        expected = "cd"
        if out != expected:
            raise check50.Failure(f"expected {expected} but found {out}")
        

@check50.check(compiles)
def find_first_char():
    '''strchr_("abcd", 'a') returns "abcd"'''
    main = r"""
int main(void)
{
    printf("%s", strchr_("abcd", 'a'));
}
"""

    with helpers.replace_main("strchr.c", main):
        check50.c.compile("strchr.c")
        out = check50.run("./strchr").stdout()
        expected = "abcd"
        if out != expected:
            raise check50.Failure(f"expected {expected} but found {out}")


@check50.check(compiles)
def find_last_char():
    '''strchr_("abcd", 'd') returns "d"'''
    main = r"""
int main(void)
{
    printf("%s", strchr_("abcd", 'd'));
}
"""

    with helpers.replace_main("strchr.c", main):
        check50.c.compile("strchr.c")
        out = check50.run("./strchr").stdout()
        expected = "d"
        if out != expected:
            raise check50.Failure(f"expected {expected} but found {out}")


@check50.check(compiles)
def find_first_char_in_duplicate():
    '''strchr_("abba", 'b') returns "bba"'''
    main = r"""
int main(void)
{
    printf("%s", strchr_("abba", 'b'));
}
"""

    with helpers.replace_main("strchr.c", main):
        check50.c.compile("strchr.c")
        out = check50.run("./strchr").stdout()
        expected = "bba"
        if out != expected:
            raise check50.Failure(f"expected {expected} but found {out}")



@check50.check(compiles)
def find_missing_char():
    '''strchr_("abcd", 'e') returns NULL'''
    main = r"""
int main(void)
{
    if (strchr_("abcd", 'e') == NULL)
    {
        printf("NULL");
    }
    else
    {
        printf("%s", strchr_("abcd", 'e'));
    }
}
"""

    with helpers.replace_main("strchr.c", main):
        check50.c.compile("strchr.c")
        out = check50.run("./strchr").stdout()
        expected = "NULL"
        if out != expected:
            raise check50.Failure(f"expected {expected} but found {out}")


@check50.check(compiles)
def find_term_char():
    '''strchr_("abcd", '\\0') returns ""'''
    main = r"""
int main(void)
{
    if (strchr_("abcd", '\0') == NULL)
    {
        printf("NULL");
    }
    else if (strcmp(strchr_("abcd", '\0'), "") == 0)
    {
        printf("great success");
    }
    else
    {
        printf("%s", strchr_("abcd", '\0'));
    }
}
"""

    with helpers.replace_main("strchr.c", main):
        check50.c.compile("strchr.c")
        out = check50.run("./strchr").stdout()
        expected = "great success"
        if out != expected:
            raise check50.Failure(f"expected \"\" but found {out}")

