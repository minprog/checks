import checkpy.entities.exception
from checkpy import *
from _default_checks import checkStyle

exclude("*")
require(file.name)

@passed(checkStyle, hide=False)
def check_create_board():
    """functie `create_board` werkt correct"""
    (declarative.function("create_board")
        .params("dim")
        .returnType(list[list[int]])
        .call(4)
        .returns([
            [15, 14, 13, 12],
            [11, 10, 9, 8],
            [7, 6, 5, 4],
            [3, 1, 2, 0],
        ])
        .call(3)
        .returns([
            [8, 7, 6],
            [5, 4, 3],
            [2, 1, 0]
        ])
    )()

@passed(check_create_board, hide=False)
def check_is_won():
    """functie `is_won` werkt correct"""
    winning_board_4 = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 14, 15, 0]
    ]

    non_winning_board_4 = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 15, 14, 0]
    ]

    winning_board_3 = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 0]
    ]

    non_winning_board_3 = [
        [1, 2, 3],
        [4, 6, 5],
        [7, 8, 0]
    ]

    (declarative.function("is_won")
        .params("board")
        .returnType(bool)
        .call(non_winning_board_3)
        .returns(False)
        .call(winning_board_3)
        .returns(True)
        .call(non_winning_board_4)
        .returns(False)
        .call(winning_board_4)
        .returns(True)
    )()

@passed(check_is_won, hide=False)
def check_move_tile():
    """functie `move_tile` werkt correct"""
    def assertMoved(fs):
        assert board == [
            [15, 14, 13, 12],
            [11, 10, 9, 8],
            [7, 6, 5, 4],
            [3, 1, 0, 2],
        ], "het bord wordt niet correct bijgewerkt na een move"

    (declarative.function("move_tile")
        .params("board", "tile")
        .returnType(bool)
        .call([
            [15, 14, 13, 12],
            [11, 10, 9, 8],
            [7, 6, 5, 4],
            [3, 1, 2, 0],
        ], 2)
        .returns(True)
        .call([
            [15, 14, 13, 12],
            [11, 10, 9, 8],
            [7, 6, 5, 4],
            [3, 1, 2, 0],
        ], 14)
        .call(
            board := [
                [15, 14, 13, 12],
                [11, 10, 9, 8],
                [7, 6, 5, 4],
                [3, 1, 2, 0],
        ], 2)
        .do(assertMoved)
    )()
    
@passed(check_move_tile, hide=False)
def check_win():
    """spel werkt en is uit te spelen"""
    steps = [
        "4", "4","5","6","1","2","4","5","6",
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
        "14","15","11","12"
    ]

    try:
        output = outputOf(stdinArgs=steps, overwriteAttributes=[("__name__", "__main__")])
    except checkpy.entities.exception.InputError:
        raise AssertionError("je programma lijkt niet te werken met de juiste oplossing voor het 4x4-board")

    lines = output.splitlines()
    last_line = lines[-1]

    assert "Gefeliciteerd" in last_line or "Congratulations" in last_line
