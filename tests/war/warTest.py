import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from checkpy import *
from _default_checks import *

import re

checkPytest.nTests = 0

exclude("*")
includeFromTests(f"test_{file.name}")
require(file.name)

class Value:
    VALUES = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
                '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    
    def __init__(self, val: str):
        self.value = val
        self.numericValue = self.VALUES[val]

    def __gt__(self, other):
        if self.numericValue == 2 and other.numericValue == 14:
            return True
        if self.numericValue == 14 and other.numericValue == 2:
            return False

        return self.numericValue > other.numericValue
    
    def __eq__(self, other):
        return self.value == other.value
    
    def __repr__(self):
        return self.value

@passed(*allDefaults, hide=False)
def testWar():
    """war werkt correct"""
    output = outputOf()
    assert output == "", "make sure your main code is wrapped by 'if __name__ == \"__main__\":'"

    output = outputOf(overwriteAttributes=[("__name__", "__main__")])
    
    rounds = output.split("\n\n")
    result = rounds.pop(-1)

    actual_round_number = 1
    actual_cards_p1 = 26
    actual_cards_p2 = 26

    for round in rounds:
        lines = round.split("\n")
        assert len(lines) == 4, "expected each round to be print exactly 4 lines of output, but found the following output:\n {round}"

        numbers = re.findall(r"\d+", lines[0])
        if not numbers:
            raise AssertionError(f"Expected a number for the round on the first line of:\n {round}")
        round_number = int(numbers[0])

        if round_number != actual_round_number:
            raise AssertionError(f"Expected Round: {actual_round_number}, but found Round: {round_number}")

        m1 = re.match(r"Player 1 draws (J|Q|K|A|[2-9]|10) of (Clubs|Diamonds|Hearts|Spades)", lines[1])
        if not m1:
            raise AssertionError(
                "expected the second line of the round to be of the form:\n"
                "Player 1 draws 10 of Clubs\n"
                "But found:\n" +
                lines[1]
            )
        player1_value = Value(m1.group(1))
        
        m2 = re.match(r"Player 2 draws (J|Q|K|A|[2-9]|10) of (Clubs|Diamonds|Hearts|Spades)", lines[2])
        if not m2:
            raise AssertionError(
                "expected the second line of the round to be of the form:\n"
                "Player 2 draws 10 of Clubs\n"
                "But found:\n" +
                lines[2]
            )
        player2_value = Value(m2.group(1))
        
        if lines[3] != "Player 1 wins this round!" and\
               lines[3] != "Player 2 wins this round!" and\
               lines[3] != "It's a tie!":
            raise AssertionError(
                "Expected the last line of each round to be either:\n"
                "    Player 1 wins this round!\n"
                "    Player 2 wins this round!\n"
                "    It's a tie!\n"
                f"But found:\n{round}"
            )

        conclusion = lines[3]

        if conclusion == "It's a tie!":
            assert player1_value == player2_value, f"expected player 1's value {player1_value} to be equal to player 2's value {player2_value} for the following round:\n{round}"
        elif conclusion == "Player 1 wins this round!":
            actual_cards_p1 += 1
            actual_cards_p2 -= 1
            assert player1_value > player2_value, f"expected player 1's value {player1_value} to be bigger than player 2's value {player2_value} for the following round:\n{round}"
        else:
            actual_cards_p2 += 1
            actual_cards_p1 -= 1
            assert player2_value > player1_value, f"expected player 2's value {player2_value} to be bigger than player 1's value {player1_value} for the following round:\n{round}"

        actual_round_number += 1

    if actual_cards_p1 == actual_cards_p2:
        assert result == "The game is a tie!\n"
    elif actual_cards_p1 > actual_cards_p2:
        assert result == f"Player 1 wins the game with {actual_cards_p1} cards!\n"
    else:
        assert result == f"Player 2 wins the game with {actual_cards_p2} cards!\n"