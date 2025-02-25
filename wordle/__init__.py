# Known limitations:
# Does not check for multiple character guesses in multiple places

import check50
import check50.c
import check50.internal
import string
from copy import deepcopy

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)
helpers.set_stdout_limit(10000)

@check50.check()
def exists():
    """wordle.c exists"""
    check50.exists("wordle.c")

@check50.check(exists)
def compiles():
    """wordle.c compiles"""
    check50.c.compile("wordle.c", lcs50=True)

@check50.check(compiles)
def rejects_wrong_guesses():
    """rejects wrong guesses (foo)"""
    check50.run("./wordle").stdin("foo").stdout("accepting 5 letter words, try again")

@check50.check(compiles)
def test_six_guess_game():
    """gives correct feedback on guesses (state, unite, apple, pears, hello, rough)"""
    test_guesses(
        "state",
        "unite",
        "apple",
        "pears",
        "hello",
        "rough"
    )
    
@check50.check(compiles)
def test_vowels():
    """gives correct feedback on guesses with only vowels (aeiou, eiouy, iouya, ouyae, uyaei, yaeio)"""
    test_guesses(
        "aeiou",
        "eiouy",
        "iouya",
        "ouyae",
        "uyaei",
        "yaeio"
    )

@check50.check(compiles)
def test_multiple_vowels():
    """gives correct feedback on guesses with multiple vowels: (aaeei, aeeii, eeiia, eiiaa, iiaae, iaaee)"""
    test_guesses(
        "aaeei",
        "aeeii",
        "eeiia",
        "eiiaa",
        "iiaae",
        "iaaee"
    )

def test_guesses(*guesses: str):
    # only one stdin call, subsequent calls would eat stdout
    # prompt=False prevents eating the first stdin prompt
    out = (check50.run("./wordle")
        .stdin("\n".join(guesses), prompt=False) 
        .stdout()
    )
    
    last_line = [strip_ansi(l) for l in out.split("\n") if l.strip()][-1].strip()
    
    if "lose" in last_line:
        if "You lose" not in last_line:
            raise check50.Failure(f"Expected:\nYou lose\n    But got:\n{last_line}")
    elif "You win" not in last_line:
        raise check50.Failure(f"Expected:\nYou win\n    But got:\n{last_line}")

    word_feedbacks = [l.lstrip("Your guess: ") for l in out.split("\n") if l.startswith("Your guess: ")]

    knowledge = WordleKnowledge()
    for feedback in word_feedbacks:
        knowledge.add_guess(feedback)

class WordleKnowledge():
    def __init__(self):
        # None = unknown
        # False = not in that spot
        # True = in that spot 
        self.letter_ops: dict[str, bool | None] = {}
        for letter in string.ascii_lowercase:
            self.letter_ops[letter] = [None] * 5

        self.guesses: list[str] = []


    def add_guess(self, guess: str):
        self.update_letter_ops(guess)
        self.guesses.append(guess)


    def update_letter_ops(self, guess: str):
        word = strip_ansi(guess)
        temp_letter_ops = deepcopy(self.letter_ops)
        states = self.parse_feedback(guess)

        for i, (letter, state) in enumerate(states):
            # Red
            if state == 0:
                if temp_letter_ops != [None] * 5:
                    # check later states for no yellow (state 1)
                    later_states = [s for j, s in enumerate(states) if j > i]
                    same_letter_states = [(l, s) for (l, s) in later_states if l == letter]

                    for _, other_state in same_letter_states:
                        if other_state == 1:
                            raise check50.Failure(
                                f"letter '{letter}' on index {i} turned red where the same letter turned yellow later in guess {guess}\x1b[39;49m\x1b[31m"
                            )

                    # check other states for min count
                    min_count = sum(1 if x == True else 0 for x in self.letter_ops[letter])
                    if (
                        min_count == 0 
                        and any(x == False for x in self.letter_ops[letter])
                        and not all(x == False for x in self.letter_ops[letter])
                    ):
                        min_count = 1

                    other_states = [s for j, s in enumerate(states) if j != i]
                    same_letter_states = [(l, s) for (l, s) in other_states if l == letter]
                    
                    this_guess_count = 0
                    for _, other_state in same_letter_states:
                        if other_state == 1 or other_state == 2:
                            this_guess_count += 1

                    if this_guess_count < min_count:
                        raise check50.Failure(
                            f"expected a minimal of {min_count} occurances of letter {letter}, but the following guess suggested less: {guess}\x1b[39;49m\x1b[31m"
                        )
                
                other_states = [s for j, s in enumerate(states) if j != i]
                same_letter_states = [(l, s) for (l, s) in other_states if l == letter]    

                # If another letter is yellow, treat this red as yellow
                if any(s == 1 for _, s in same_letter_states):
                    temp_letter_ops[letter][i] == False
                # Otherwise, simply as red
                else:
                    for j, op in enumerate(temp_letter_ops[letter]):
                        if op is None:
                            temp_letter_ops[letter][j] = False

            # Yellow
            elif state == 1:
                if self.letter_ops[letter][i] == True:
                    raise check50.Failure(
                        f"{guess}\x1b[39;49m\x1b[31m shows {letter} on index {i} to be in the wrong place, but an earlier guess marked it as correct: {self.guesses_pprint()}"
                    )
                temp_letter_ops[letter][i] = False

            # Green
            elif state == 2:
                if self.letter_ops[letter][i] == False:
                    raise check50.Failure(
                        f"{guess}\x1b[39;49m\x1b[31m shows {letter} on index {i} to be correct, but an earlier guess marked it as wrong: {self.guesses_pprint()}"
                    )
                temp_letter_ops[letter][i] = True

        self.letter_ops = temp_letter_ops

    def guesses_pprint(self) -> str:
        return ", ".join([g + "\x1b[39;49m" for g in self.guesses])

    def parse_feedback(self, feedback: str) -> list[tuple[str, int]]:
        """
        Parse feedback on word
        Returns list of tuples for each letter and 0, 1, 2
        0 = not in word
        1 = misplaced
        2 = correct
        """
        states: list[tuple[str, int]] = []

        state = -1
        while feedback:
            if feedback[0] == "\x1b": # escape
                # Red
                if feedback.startswith("\x1b[31m"):
                    feedback = feedback[len("\x1b[31m"):]
                    state = 0
                elif feedback.startswith("\x1b[0;31m"):
                    feedback = feedback[len("\x1b[0;31m"):]
                    state = 0
                # Green
                elif feedback.startswith("\x1b[32m"):
                    feedback = feedback[len("\x1b[32m"):]
                    state = 2
                elif feedback.startswith("\x1b[0;32m"):
                    feedback = feedback[len("\x1b[0;32m"):]
                    state = 0
                # Yellow
                elif feedback.startswith("\x1b[33m"):
                    feedback = feedback[len("\x1b[33m"):]
                    state = 1
                elif feedback.startswith("\x1b[0;33m"):
                    feedback = feedback[len("\x1b[0;33m"):]
                    state = 0
                # Reset
                elif feedback.startswith("\x1b[39;49m"):
                    feedback = feedback[len("\x1b[39;49m"):]
                    state = -1
                elif feedback.startswith("\x1b[0m"):
                    feedback = feedback[len("\x1b[0m"):]
                    state = -1
            else:
                letter = feedback[0]
                feedback = feedback[1:]
            
                states.append((letter, state))
        return states

def strip_ansi(s: str) -> str:
    return (s
        .strip()
        .replace("\x1b[31m", "")
        .replace("\x1b[32m", "")
        .replace("\x1b[33m", "")
        .replace("\x1b[39;49m", "")
    )
