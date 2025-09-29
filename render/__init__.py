import check50
import check50.c
import check50.internal

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)

@check50.check()
def exists():
    "render.c exists"
    check50.exists("render.c")

@check50.check(exists)
def compiles():
    "render.c compiles"
    check50.c.compile("render.c", lcs50=True)

@check50.check(compiles)
def has_functions():
    "render.c has all required functions"
    with open("render.c") as f:
        content = f.read()

    for name in ["max", "render", "stretch", "interlace", "combine"]:
        if f" {name}(" not in content and f" {name} (" not in content:
            raise check50.Failure(f"Missing function: {name}")

@check50.check(has_functions)
def test_max():
    "max() returns correct maximum"
    main = r"""
int main(void)
{
    int image1[] = {1, 3, 5, 3, 1};
    int height1 = 5;
    printf("Max of 1, 3, 5, 3, 1 = %d\n", max(image1, height1));

    int image2[] = {3, 2, 1};
    int height2 = 3;
    printf("Max of 3, 2, 1 = %d\n", max(image2, height2));

    int image3[] = {1, 2, 3, 4};
    int height3 = 4;
    printf("Max of 1, 2, 3, 4 = %d\n", max(image3, height3));
}
"""
    with helpers.replace_main("render.c", main):
        check50.c.compile("render.c", lcs50=True)

        (check50.run("./render")
            .stdout("Max of 1, 3, 5, 3, 1 = 5")
            .stdout("Max of 3, 2, 1 = 3")
            .stdout("Max of 1, 2, 3, 4 = 4")
        )


@check50.check(has_functions)
def test_render():
    "render() prints correct output"
    main = r"""
int main(void)
{
    int image1[] = {1, 3, 5};
    render(image1, 3);

    int image2[] = {2, 4, 2};
    render(image2, 3);

    int image3[] = {3, 3, 3};
    render(image3, 3);
}
"""
    with helpers.replace_main("render.c", main):
        check50.c.compile("render.c", lcs50=True)

        (check50.run("./render")
            .stdout("  #\n", regex=False)
            .stdout(" ###\n", regex=False)
            .stdout("#####\n", regex=False)
            .stdout(" ##\n", regex=False)
            .stdout("####\n", regex=False)
            .stdout(" ##\n", regex=False)
            .stdout("###\n", regex=False)
            .stdout("###\n", regex=False)
            .stdout("###\n", regex=False)
        )


@check50.check(has_functions)
def test_stretch():
    "stretch() multiplies row lengths correctly"
    main = r"""
int main(void)
{
    int image1[] = {1, 3, 5};
    stretch(image1, 3, 2);
    render(image1, 3);

    int image2[] = {2, 4, 6};
    stretch(image2, 3, 3);
    render(image2, 3);
}
"""
    with helpers.replace_main("render.c", main):
        check50.c.compile("render.c", lcs50=True)

        (check50.run("./render")
            .stdout("    ##\n", regex=False)
            .stdout("  ######\n", regex=False)
            .stdout("##########\n", regex=False)
            .stdout("      ######\n", regex=False)
            .stdout("   ############\n", regex=False)
            .stdout("##################\n", regex=False)
        )

@check50.check(has_functions)
def test_interlace():
    "interlace() zeroes out every second row"
    main = r"""
int main(void)
{
    int image1[] = {1, 3, 5, 7, 9};
    interlace(image1, 5);
    render(image1, 5);

    int image2[] = {2, 2, 2, 2};
    interlace(image2, 4);
    render(image2, 4);
}
"""
    with helpers.replace_main("render.c", main):
        check50.c.compile("render.c", lcs50=True)

        (check50.run("./render")
            .stdout("    #\n", regex=False)
            .stdout("\n", regex=False)
            .stdout("  #####\n", regex=False)
            .stdout("\n", regex=False)
            .stdout("#########\n", regex=False)
            .stdout("##\n", regex=False)
            .stdout("\n", regex=False)
            .stdout("##\n", regex=False)
            .stdout("\n", regex=False)
        )

@check50.check(has_functions)
def test_combine():
    "combine() merges two arrays using max row lengths"
    main = r"""
int main(void)
{
    int image1[] = {1, 5, 9};
    int image2[] = {5, 3, 1};
    combine(image1, image2, 3);
    render(image1, 3);

    int a[] = {1, 2, 3};
    int b[] = {3, 2, 1};
    combine(a, b, 3);
    render(a, 3);

    int x[] = {6, 6, 6};
    int y[] = {2, 8, 4};
    combine(x, y, 3);
    render(x, 3);
}
"""
    with helpers.replace_main("render.c", main):
        check50.c.compile("render.c", lcs50=True)

        (check50.run("./render")
            .stdout("  #####\n", regex=False)
            .stdout("  #####\n", regex=False)
            .stdout("#########\n", regex=False)
            .stdout("###\n", regex=False)
            .stdout("##\n", regex=False)
            .stdout("###\n", regex=False)
            .stdout(" ######\n", regex=False)
            .stdout("########\n", regex=False)
            .stdout(" ######\n", regex=False)
        )
