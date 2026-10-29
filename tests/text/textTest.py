import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent))

from checkpy import *
from _default_checks import checkMypy, checkStyle
from _helpers import runPythonTool


def analyzeText(content: str) -> str:
    """Run text.py with a text.txt containing content, and return its output."""
    exclude("*")
    include("text.py")

    with open("text.txt", "w") as tempFile:
        tempFile.write(content)

    # argv is not used by text.py, but it makes sure checkpy does not
    # reuse the cached output of a previous run with a different text.txt
    output = outputOf(
        argv=["text.py", content],
        overwriteAttributes=[("__name__", "__main__")]
    )
    return output.strip()


@passed(checkStyle, checkMypy, hide=False)
def testEmptyFile():
    """an empty text.txt results in "No words found."."""
    assert analyzeText("") == \
"""TEXT ANALYZER
No words found."""


@passed(testEmptyFile, hide=False)
def testStopwordsAndApostrophes():
    """stopwords are not counted as common words, apostrophes are removed ("cat's" becomes "cats")."""
    content = "The cat and the hat.\nIt is the cat's hat, and that is that!\n"
    assert analyzeText(content) == \
"""TEXT ANALYZER
Total words: 14
Unique words: 8
Longest word: cats
Shortest word: it
Long words: 0
Words used once: 2
Most common words:
hat         ##
cat         #
cats        #"""


@passed(testEmptyFile, hide=False)
def testTopFiveAndTies():
    """only the five most common words are shown, ties are resolved by order of first appearance."""
    content = (
        "Zebra apple mango apple zebra kiwi\n"
        "banana Mango, mango! papaya... pomegranate; Cherry cherry cherry cherry\n"
    )
    assert analyzeText(content) == \
"""TEXT ANALYZER
Total words: 15
Unique words: 8
Longest word: pomegranate
Shortest word: kiwi
Long words: 1
Words used once: 4
Most common words:
cherry      ####
mango       ###
zebra       ##
apple       ##
kiwi        #"""


@passed(testEmptyFile, hide=False)
def testLongerText():
    """a longer text with punctuation and quotes is analyzed correctly."""
    content = (
        'The fox jumped over the fence, and the dog watched it go. '
        '"That fox is clever," said the farmer\'s wife.\n'
        'It was a quiet evening in the village; the fox was gone and the dog was asleep.\n'
        'Clever foxes never return to the same fence twice, she said, but this fox always did.\n'
    )
    assert analyzeText(content) == \
"""TEXT ANALYZER
Total words: 53
Unique words: 35
Longest word: watched
Shortest word: a
Long words: 4
Words used once: 20
Most common words:
fox         ####
fence       ##
dog         ##
clever      ##
said        ##"""


@passed(testStopwordsAndApostrophes, testTopFiveAndTies, testLongerText, hide=False)
def testCyclomaticComplexity():
    """flake8 --max-complexity=3 --select=C text.py shows no violations"""
    result = runPythonTool("flake8", ["--max-complexity=3", "--select=C", file])
    assert "C901" not in result.stdout
