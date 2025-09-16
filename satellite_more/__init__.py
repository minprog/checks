import check50
import check50.c
import check50.internal

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)

@check50.check()
def exists():
    "satellite.c exists"
    check50.exists("satellite.c")

@check50.check(exists)
def compiles():
    "satellite.c compiles"
    check50.c.compile("satellite.c", lcs50=True)

@check50.check(compiles)
def has_functions():
    "satellite.c has all required functions"
    with open("satellite_more.c") as f:
        content = f.read()

    for name in ["fix_multiple_missing_values"]:
        if f" {name}(" not in content and f" {name} (" not in content:
            raise check50.Failure(f"Missing function: {name}")

@check50.check(has_functions)
def test_fix_multiple_missing_values():
    "test_fix_multiple_missing_values() correctly replaces any missing values"
    main = r"""
int main(void)
{
    int values1[] = {1, -1, 3};
    fix_multiple_missing_values(values1, 3);
    for (int i = 0; i < 3; i++)
    {
        printf("%d, ", values1[i]);
    }
    printf("\n");

    int values2[] = {2, -1, 0, -1, 2};
    fix_multiple_missing_values(values2, 5);
    for (int i = 0; i < 5; i++)
    {
        printf("%d, ", values2[i]);
    }
    printf("\n");
    
    int values3[] = {2, 2, -1, 3};
    fix_multiple_missing_values(values3, 4);
    for (int i = 0; i < 4; i++)
    {
        printf("%d, ", values3[i]);
    }
    printf("\n");

    int values4[] = {-1, -1, 3, 7, -1};
    fix_multiple_missing_values(values4, 5);
    for (int i = 0; i < 5; i++)
    {
        printf("%d, ", values4[i]);
    }
    printf("\n");

    int values5[] = {-1, -1, -1, -1};
    fix_multiple_missing_values(values5, 4);
    for (int i = 0; i < 4; i++)
    {
        printf("%d, ", values5[i]);
    }
    printf("\n");

    int values6[] = {1, -1, -1, 8, -1, 6};
    fix_multiple_missing_values(values6, 6);
    for (int i = 0; i < 6; i++)
    {
        printf("%d, ", values6[i]);
    }
    printf("\n");
}
"""
    with helpers.replace_main("satellite_more.c", main):
        check50.c.compile("satellite_more.c", lcs50=True)

        try:
            (check50.run("./satellite_more")
                .stdout("1, 2, 3, \n", regex=False)
                .stdout("2, 1, 0, 1, 2, \n", regex=False)
                .stdout("2, 2, 2, 3, \n", regex=False)
                .stdout("3, 3, 3, 7, 7, \n", regex=False)
                .stdout("-1, -1, -1, -1, \n", regex=False)
                .stdout("1, 3, 5, 8, 7, 6, \n", regex=False)
            )
        except check50.Failure as f:
            f.payload["rationale"] = f.payload["rationale"] + f"\nthe following main function was used:\n{main}"
            raise f
