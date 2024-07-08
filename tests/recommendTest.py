from checkpy import *
from _default_checks import *
from _helpers import testPytestFail
import os

checkPytest.nTests = 8

exclude("*")
require(file.name, f"test_{file.name}")

@passed(*allDefaults, hide=False)
def testConvertToWords():
    """convert_to_words works correctly"""
    (declarative.function("convert_to_words")
        .params("text")
        .returnType(set[str])
        .call("Hello, world!").returns({"hello", "world"})
        .call("Hello world").returns({"hello", "world"})
        .call("").returns(set())
        .call("This is a test").returns({"this", "is", "a", "test"})
    )()

@passed(*allDefaults, hide=False)
def testComputeJaccardIndex():
    """compute_jaccard_index works correctly"""
    (declarative.function("compute_jaccard_index")
        .params("text1", "text2")
        .returnType(float)
        .call("Hello world", "Hello there").returns(approx(1/3))
        .call("Hello", "Hello").returns(approx(1.0))
        .call("Hello", "World").returns(approx(0.0))
    )()

@passed(*allDefaults, hide=False)
def testRecommend():
    """recommend works correctly"""
    (declarative.function("recommend")
        .params("script_name", "scripts")
        .returnType(str)
        
        # Test with similar scripts
        .call("elvis.txt", {
            'elvis.txt': 'Elvis is a biographical drama film',
            'joker.txt': 'Joker is about a villain in Gotham',
            'magnolia.txt': 'Magnolia is an ensemble drama film',
            'lalaland.txt': 'La La Land is a musical romance'
        }).returns("magnolia.txt")

        # Test with clear similarity
        .call("frozen.txt", {
            'frozen.txt': 'Anna and Elsa embark on a journey across snowy landscapes',
            'up.txt': 'Carl and Russell go on an adventure to South America',
            'her.txt': 'A man falls in love with his AI operating system',
            'interstellar.txt': 'Astronauts travel through a wormhole in space'
        }).returns("up.txt")

        # Test with diverse content
        .call("interstellar.txt", {
            'interstellar.txt': 'Astronauts travel through a wormhole in space and time',
            'tenet.txt': 'A secret agent embarks on a time bending mission',
            'joker.txt': 'Joker is about a villain from Gotham',
            'her.txt': 'A man falls in love with his AI operating system'
        }).returns("tenet.txt")

        # Test with empty script content
        .call("empty.txt", {
            'empty.txt': '',
            'joker.txt': 'Joker is about a villain in Gotham',
            'her.txt': 'A man falls in love with his AI operating system',
            'up.txt': 'Carl and Russell go on an adventure to South America'
        }).returns("joker.txt")

        # Test with minimal content
        .call("minimal.txt", {
            'minimal.txt': 'Adventure',
            'joker.txt': 'Joker',
            'her.txt': 'AI love',
            'up.txt': 'Adventure'
        }).returns("up.txt")
    )()


@passed(testRecommend, hide=False)
def testTests():
    """pytest tests fail for various incorrect implementations"""
    def convert_to_words(text):
        # correct implementation of convert_to_words
        new_text = ""
        for char in text:
            if char.isalpha():
                new_text += char
            else:
                new_text += " "
        
        return set(new_text.lower().split())

    def compute_jaccard_index(text1, text2):
        # correct implementation of compute_jaccard_index
        words1 = convert_to_words(text1)
        words2 = convert_to_words(text2)
        return len(words1 & words2) / len(words1 | words2)

    def get_scripts(filepath):
        # correct implementation of get_scripts
        scripts = {}
        for filename in os.listdir(filepath):
            with open("filename") as f:
                scripts[filename] = f.read()
        return scripts

    def recommend(script_name, scripts):
        # correct implementation of recommend
        base_script = scripts[script_name]
        best_match = None
        best_score = 0.0
        for name, content in scripts.items():
            if name != script_name:
                score = compute_jaccard_index(base_script, content)
                if score > best_score:
                    best_score = score
                    best_match = name
        return best_match

    correct_convert_to_words = convert_to_words
    correct_compute_jaccard_index = compute_jaccard_index
    correct_get_scripts = get_scripts
    correct_recommend = recommend

    # Incorrect implementations for testing
    def convert_to_words(text):
        # incorrect implementation of convert_to_words that does nothing
        pass
    testPytestFail(convert_to_words, correct_compute_jaccard_index, correct_get_scripts, correct_recommend)

    def convert_to_words(text):
        # incorrect implementation of convert_to_words that returns words as a list
        return text.lower().split()
    testPytestFail(convert_to_words, correct_compute_jaccard_index, correct_get_scripts, correct_recommend)
    
    def compute_jaccard_index(text1, text2):
        # incorrect implementation of compute_jaccard_index that returns 0.5 for everything
        return 0.5
    testPytestFail(correct_convert_to_words, compute_jaccard_index, correct_get_scripts, correct_recommend)

    def compute_jaccard_index(text1, text2):
        # incorrect implementation of compute_jaccard_index that returns 1 for everything
        return 1.0
    testPytestFail(correct_convert_to_words, compute_jaccard_index, correct_get_scripts, correct_recommend)
    
    def recommend(script_name, scripts):
        # incorrect implementation of recommend that always returns the same script
        return 'joker.txt'
    testPytestFail(correct_convert_to_words, correct_compute_jaccard_index, correct_get_scripts, recommend)

    def recommend(script_name, scripts):
        # incorrect implementation of recommend that returns None
        return None
    testPytestFail(correct_convert_to_words, correct_compute_jaccard_index, correct_get_scripts, recommend)

    def recommend(script_name, scripts):
        # incorrect implementation of recommend that returns the given script itself
        return script_name
    testPytestFail(correct_convert_to_words, correct_compute_jaccard_index, correct_get_scripts, recommend)

    def recommend(script_name, scripts):
        # incorrect implementation of recommend that returns a hardcoded value
        return "elvis.txt"
    testPytestFail(correct_convert_to_words, correct_compute_jaccard_index, correct_get_scripts, recommend)
