import check50
import check50.c
import re


@check50.check()
def exists():
    """tiles.c exists."""
    check50.exists("tiles.c")


@check50.check(exists)
def compiles():
    """tiles.c compiles."""
    with open("tiles.c", "r") as f:
        content = f.read()
    
    # Remove sleeps from student code
    match = re.compile("#include\s*<unistd\.h>").search(content)
    if match:
        with open("tiles.c", "w") as f:
            content = content[:match.end()] + "\n#define usleep(x)" + content[match.end():]
            f.write(content)
        
    check50.run("make").exit(0)


@check50.check(compiles)
def init3():
    """initializes a 3x3 board correctly."""
    check = check50.run("./tiles 3")
    
    board = [
        [8, 7, 6],
        [5, 4, 3],
        [2, 1, 0]
    ]
    check_board(check, board)


@check50.check(compiles)
def init4():
    """initializes a 4x4 board correctly."""
    check = check50.run("./tiles 4")
    
    # check for fully correct board
    correct_board = [
        [15, 14, 13, 12],
        [11, 10, 9, 8],
        [7, 6, 5, 4],
        [3, 1, 2, 0]
    ]
    
    try:
        check_board(check, correct_board)
    except check50.Failure as f:
        # check for board without swapped tiles
        invalid_board = [
            [15, 14, 13, 12],
            [11, 10, 9, 8],
            [7, 6, 5, 4],
            [3, 2, 1, 0]
        ]

        check = check50.run("./tiles 4")

        try:    
            check_board(check, invalid_board)
        except check50.Failure:
            pass
        else:
            raise check50.Failure("board initialized incorrectly", help="did you remember to swap the last two tiles?")

        raise f


@check50.check(init3)
def invalid():
    """3x3 board: catches moving 2, 4, 5, 6, 7, 8 as illegal moves."""
    moves = ["2", "4", "5", "6", "7", "8"]

    check = check50.run("./tiles 3")

    for move in moves:
        check.stdin(move).stdout("Illegal move.")

    board = [
        [8, 7, 6],
        [5, 4, 3],
        [2, 1, 0]
    ]

    check_board(check, board)


@check50.check(init3)
def move_up2():
    """3x3 board: move blank up twice."""
    check = check50.run("./tiles 3").stdin("3")
    
    board = [
        [8, 7, 6],
        [5, 4, 0],
        [2, 1, 3]
    ]
    check_board(check, board)

    check.stdin("6")
    
    board = [
        [8, 7, 0],
        [5, 4, 6],
        [2, 1, 3]
    ]
    check_board(check, board)


@check50.check(init3)
def move_left2():
    """3x3 board: move blank left twice."""
    check = check50.run("./tiles 3").stdin("1")
    
    board = [
        [8, 7, 6],
        [5, 4, 3],
        [2, 0, 1]
    ]
    check_board(check, board)

    check.stdin("2")
    
    board = [
        [8, 7, 6],
        [5, 4, 3],
        [0, 2, 1]
    ]
    check_board(check, board)


@check50.check(init3)
def move_left_right():
    """3x3 board: move blank left then right."""
    check = check50.run("./tiles 3").stdin("1")
    
    board = [
        [8, 7, 6],
        [5, 4, 3],
        [2, 0, 1]
    ]
    check_board(check, board)

    check.stdin("1")
    
    board = [
        [8, 7, 6],
        [5, 4, 3],
        [2, 1, 0]
    ]
    check_board(check, board)


@check50.check(init3)
def move_up_down():
    """3x3 board: move blank up then down."""
    check = check50.run("./tiles 3").stdin("3")
    
    board = [
        [8, 7, 6],
        [5, 4, 0],
        [2, 1, 3]
    ]
    check_board(check, board)
    
    check.stdin("3")
    
    board = [
        [8, 7, 6],
        [5, 4, 3],
        [2, 1, 0]
    ]
    check_board(check, board)
    

@check50.check(init3)
def invalid_center():
    """3x3 board: move blank left (tile 1) then up (tile 4), then try to move tiles 1, 2, 6, 8"""
    # move 1
    check = check50.run("./tiles 3").stdin("1")

    # check resulting board
    board = [
        [8, 7, 6],
        [5, 4, 3],
        [2, 0, 1]
    ]
    check_board(check, board)

    # move 4
    check.stdin("4")

    # check resulting board
    board = [
        [8, 7, 6],
        [5, 0, 3],
        [2, 4, 1]
    ]
    check_board(check, board)

    # try moving all corner tiles
    for move in ["1", "2", "6", "8"]:
        check.stdin(move).stdout("Illegal move.")

    # check that board state didn't change
    check_board(check, board)
    

@check50.check(init3)
def solve3():
    """solves a 3x3 board."""
    steps = ["3","4","1","2","5","8","7","6",
             "4","1","2","5","8","7","6","4",
             "1","2","4","1","2","3","5","4",
             "7","6","1","2","3","7","4","8",
             "6","4","8","5","7","8","5","6",
             "4","5","6","7","8","6","5","4",
             "7","8"]

    check = check50.run("./tiles 3")

    for step in steps:
        check.stdout("Tile to move:")
        check.stdin(step, prompt=False)

    board = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 0]
    ]
    check_board(check, board)
    check.stdout("ftw!")


@check50.check(init4)
def solve4():
    """solves a 4x4 board."""
    steps = ["4","5","6","1","2","4","5","6",
             "1","2","3","7","11","10","9","1",
             "2","3","4","5","6","8","1","2",
             "3","4","7","11","10","9","14",
             "13","12","1","2","3","4","14",
             "13","12","1","2","3","4","14",
             "13","12","1","2","3","4","12",
             "9","15","1","2","3","4","12","9",
             "13","14","9","13","14","7","5",
             "9","13","14","15","10","11","5",
             "9","13","7","11","5","9","13",
             "7","11","15","10","5","9","13",
             "15","11","8","6","7","8","14",
             "12","6","7","8","14","12","6",
             "7","8","14","15","11","10","6",
             "7","8","12","15","11","10","15",
             "11","14","12","11","15","10",
             "14","15","11","12"]

    check = check50.run("./tiles 4")

    for step in steps:
        check.stdout("Tile to move:")
        check.stdin(step, prompt=False)

    board = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 14, 15, 0]
    ]
    check_board(check, board)
    check.stdout("ftw!")


def check_board(check, board):
    """Helper function to check that each row of the board is correct"""
    for row in board:
        row_regex = "[^\n]+".join(str(n) if n != 0 else "[_0]" for n in row) + "[^\n]*\n"
        row_str = "    ".join(str(n).rjust(2) for n in row)
        check.stdout(row_regex, str_output=row_str)