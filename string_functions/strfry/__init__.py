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
def no_malloc():
    """malloc() is not used for strfry"""
    with open("strfry.c") as f:
        content = f.read()

        for i, line in enumerate(content.split("\n")):
            if "malloc" in line:
                line_nr = i + 1
                raise check50.Failure(f"found malloc on line {line_nr}: {line}")


@check50.check(exists)
def scrambles2():
    '''strfry_ can scramble "ab" to "ab" and "ba"'''
    main = r"""
int main(void)
{
    char s[3];
    s[0] = 'a';
    s[1] = 'b';
    s[2] = '\0';
    
    srand48(0);

    for (int i = 0; i < 100; i++)
    {
        printf("%s\n", strfry_(s));
    }
}
"""

    with helpers.replace_main("strfry.c", main):
        with open("strfry.c") as f:
            content = f.read()
            
        if "#define _XOPEN_SOURCE" not in content and "drand48" in content:
            with open("strfry.c", "w") as f:
                f.write("#define _XOPEN_SOURCE\n" + content)
        
        check50.c.compile("strfry.c")
        check50.run("./strfry").stdout("ab").stdout("ba").exit(0)


@check50.check(exists)
def scrambles3():
    '''strfry_ can scramble "123" to all its permutations'''
    main = r"""
    int main(void)
    {
        char s[3];
        s[0] = 'a';
        s[1] = 'b';
        s[2] = '\0';

        srand48(0);

        for (int i = 0; i < 1000; i++)
        {
            printf("%s\n", strfry_(s));
        }
    }
    """

    perms = ["".join(perm) for perm in itertools.permutations("123")]

    with helpers.replace_main("strfry.c", main):
        with open("strfry.c") as f:
            content = f.read()
            
        if "#define _XOPEN_SOURCE" not in content and "drand48" in content:
            with open("strfry.c", "w") as f:
                f.write("#define _XOPEN_SOURCE\n" + content)

        check50.c.compile("strfry.c")
        out = check50.run("./strfry").stdout()

        for perm in perms:
            check50.log(f"checking for {perm} in output")
            if perm not in out:
                check50.Failure(f"Missing {perm}")
