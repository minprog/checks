import check50
import check50.c
import check50.internal

import itertools

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../../helpers/helpers.py"
)
helpers.set_stdout_limit(10000)


@check50.check()
def exists():
    """strfry.c exists"""
    check50.exists("strfry.c")


@check50.check(exists)
def compiles():
    """strfry.c compiles"""
    check50.c.compile("strfry.c", lcs50=True)


@check50.check(compiles)
def scrambles2():
    '''strfry_ can scramble "ab" to "ab" and "ba"'''
    main = r"""
int main(void)
{
    char s[3];
    s[0] = 'a';
    s[1] = 'b';
    s[2] = '\0';

    for (int i = 0; i < 100; i++)
    {
        printf("%s\n", strfry_(s));
    }
}
"""

    with helpers.replace_main("strfry.c", main):
        check50.c.compile("strfry.c")
        check50.run("./strfry").stdout("ab").stdout("ba").exit(0)


@check50.check(compiles)
def scrambles3():
    '''strfry_ can scramble "123" to all its permutations'''
    main = r"""
    int main(void)
    {
        char s[3];
        s[0] = 'a';
        s[1] = 'b';
        s[2] = '\0';

        for (int i = 0; i < 1000; i++)
        {
            printf("%s\n", strfry_(s));
        }
    }
    """

    perms = ["".join(perm) for perm in itertools.permutations("123")]

    with helpers.replace_main("strfry.c", main):
        check50.c.compile("strfry.c")
        out = check50.run("./strfry").stdout()

        for perm in perms:
            check50.log(f"checking for {perm} in output")
            if perm not in out:
                check50.Failure(f"Missing {perm}")