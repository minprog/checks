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
    """cut.c exists"""
    check50.exists("cut.c")

@check50.check(exists)
def compiles():
    """cut.c compiles"""
    check50.c.compile("cut.c", lcs50=True)

@check50.check(compiles)
def test_cut_second_column():
    """./cut -f2 telefoon.txt prints the exact same as cut -f2 -d , telefoon.txt"""
    content = (
        "Rory,+31655551938,rory@hotmail.za\n"
        "Wes,+31655551121,w.dubb@google.com\n"
        "Tanisha,+31655559831,me@tanisha.nl\n"
        "Reuben,+31655554102,reub@gmx.de\n"
    )
    with open("telefoon.txt", "w") as f:
        f.write(content)

    out_real = check50.run("./cut -f2 telefoon.txt").stdout()
    out_expected = check50.run("cut -f2 -d , telefoon.txt").stdout()
    assert_same(out_expected, out_real, "telefoon.txt", content)

@check50.check(compiles)
def test_cut_third_column():
    """./cut -f3 telefoon.txt prints the exact same as cut -f3 -d , telefoon.txt"""
    content = (
        "Rory,+31655551938,rory@hotmail.za\n"
        "Tanisha,+31655559831,me@tanisha.nl\n"
        "Reuben,+31655554102,reub@gmx.de\n"
    )
    with open("telefoon.txt", "w") as f:
        f.write(content)

    out_real = check50.run("./cut -f3 telefoon.txt").stdout()
    out_expected = check50.run("cut -f3 -d , telefoon.txt").stdout()
    assert_same(out_expected, out_real, "telefoon.txt", content)

@check50.check(compiles)
def test_cut_non_existing_column():
    """./cut -f1000 telefoon.txt prints the exact same as cut -f1000 -d , telefoon.txt"""
    content = (
        "Rory,+31655551938,rory@hotmail.za\n"
        "Wes,+31655551121,w.dubb@google.com\n"
        "Tanisha,+31655559831,me@tanisha.nl\n"
        "Reuben,+31655554102,reub@gmx.de\n"
        "Tanisha,+31655559831,me@tanisha.nl\n"
        "Reuben,+31655554102,reub@gmx.de\n"
    )
    with open("telefoon.txt", "w") as f:
        f.write(content)

    out_real = check50.run("./cut -f1000 telefoon.txt").stdout()
    out_expected = check50.run("cut -f1000 -d , telefoon.txt").stdout()
    assert_same(out_expected, out_real, "telefoon.txt", content)

def assert_same(expected: str, real: str, filename: str, file_contents: str):
    if expected != real:
        msg = f"With {filename} containing:\n{file_contents}\n    Expected:\n{expected}\n    But got:\n{real}"
        raise check50.Failure(msg)