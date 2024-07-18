import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent))

import checkpy
from checkpy import *
from _default_checks import checkMypy, checkStyle
from _helpers import runPythonTool

@passed(checkStyle, checkMypy, hide=False)
def testHangmanAllCorrectGuesses():
    """playing hangman with dictionary.txt containing just "hello" and guessing "h", "e", "l", "l", "o" works as expected."""
    # Create a new sandbox with just hangman.py in it
    exclude("*")
    include("hangman.py")

    WORD = "hello"

    # Create a temporary file and write "hello" to it
    with open("dictionary.txt", 'w') as tempFile:
        tempFile.write(f'{WORD}\n')

    output = outputOf(
        overwriteAttributes=[("__name__", "__main__")],
        stdinArgs=[
            str(len(WORD)), # word length
            "10", # guesses allowed
            *"hello", # guesses
            *"thisshouldnotbeconsumed" # feeding it anyway, the assert below gives better feedback
        ]
    )

    assert output.strip() == \
"""WELCOME TO HANGMAN ツ
I have a word in my mind of 5 letters.
It's in the word! :)
h____
It's in the word! :)
he___
It's in the word! :)
hell_
It's in the word! :)
hello
Whoa, you won!!!"""

@passed(testHangmanAllCorrectGuesses, hide=False)
def testHangmanAllWrongGuesses():
    """playing hangman with dictionary.txt containing just "foo" and guessing "b", "a", "r" works as expected."""
    # Create a new sandbox with just hangman.py in it
    exclude("*")
    include("hangman.py")

    WORD = "foo"

    # Create a temporary file and write "foo" to it
    with open("dictionary.txt", 'w') as tempFile:
        tempFile.write(f'{WORD}\n')

    output = outputOf(
        overwriteAttributes=[("__name__", "__main__")],
        stdinArgs=[
            str(len(WORD)), # word length
            "3", # guesses allowed
            *"bar", # guesses
            *"thisshouldnotbeconsumed" # feeding it anyway, the assert below gives better feedback
        ]
    )

    assert output.strip() == \
"""WELCOME TO HANGMAN ツ
I have a word in my mind of 3 letters.
That's not in the word :(
___
That's not in the word :(
___
That's not in the word :(
___
Sad, you lost ¯\_(ツ)_/¯. This was your word: foo"""


@passed(testHangmanAllCorrectGuesses, testHangmanAllWrongGuesses, hide=False)
def testCyclomaticComplexity():
    """flake8 --max-complexity=3 --select=C hangman.py shows no violations"""
    result = runPythonTool("flake8", ["--max-complexity=3", "--select=C", file])
    assert "C901" not in result.stdout