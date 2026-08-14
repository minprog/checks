"""Measure whether looking up a word gets slower as the dictionary grows.

A hash table searches one bucket, so its lookups cost the same whatever the
size of the dictionary. A linked list walks the whole thing. See scaling() in
__init__.py for how the numbers are judged.
"""

import os
import random
import re
import subprocess

# Two dictionaries, one 50x the other, and a text of words present in both
N_LARGE = 50000
N_SMALL = 1000
N_LOOKUPS = 20000
STRIDE = N_LARGE // N_SMALL
SEED = 20260814

# Files that are ours, not the student's
SKIP_SOURCES = {"speller.c", "speller_bench.c"}


WORD_LENGTH = 6

# Spread the words over the whole a-z space instead of taking the first N in
# order. Counting 0, 1, 2, ... would make every word start with an "a", which
# turns a table that hashes on the first letter into one long chain and makes
# it look exactly like a linked list.
SPACE = 26 ** WORD_LENGTH
SPREAD = SPACE // N_LARGE


def _word(number, length=WORD_LENGTH):
    """Encode a number as a fixed-length word of a-z.

    Fixed length and base 26 means the words come out unique and already in
    alphabetical order, so no sorting or duplicate check is needed.
    """
    letters = []
    for _ in range(length):
        letters.append(chr(ord("a") + number % 26))
        number //= 26
    return "".join(reversed(letters))


def generate(directory="bench"):
    """Write the two dictionaries and the text. Deterministic."""
    os.makedirs(directory, exist_ok=True)

    large = [_word(i * SPREAD) for i in range(N_LARGE)]

    # Every STRIDE'th word, so a word from the text sits at a random depth in
    # a linked list rather than clustering at one end
    small = large[::STRIDE]

    with open(os.path.join(directory, "large"), "w") as f:
        f.write("\n".join(large) + "\n")
    with open(os.path.join(directory, "small"), "w") as f:
        f.write("\n".join(small) + "\n")

    # Only words that are in both dictionaries: a miss would force a full
    # bucket scan, which punishes a small-bucket table far more than a big one
    rng = random.Random(SEED)
    words = [rng.choice(small) for _ in range(N_LOOKUPS)]
    with open(os.path.join(directory, "text"), "w") as f:
        for i in range(0, N_LOOKUPS, 10):
            f.write(" ".join(words[i:i + 10]) + "\n")


def sources(directory="."):
    """The student's own .c files, minus any that carry their own main."""
    found = []
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".c") or name in SKIP_SOURCES:
            continue
        with open(os.path.join(directory, name), errors="replace") as f:
            content = f.read()
        # A leftover file with its own main would break the link
        if re.search(r"^\s*(?:int|void)\s+main\s*\(", content, re.M):
            continue
        found.append(name)
    return found


def build(directory="."):
    """Compile the benchmark against the student's code.

    Deliberately does not use the student's Makefile: it has no target for this
    binary. Compiling every one of their .c files covers both the case where
    they kept the standard Makefile and the case where they split their code
    over several files. Returns (ok, command, output).
    """
    command = ("clang -O0 -std=c11 -Qunused-arguments -w -o speller_bench "
               "speller_bench.c " + " ".join(sources(directory)) + " -lm")
    result = subprocess.run(command, shell=True, cwd=directory,
                            capture_output=True, text=True, timeout=120)
    return result.returncode == 0, command, (result.stdout + result.stderr).strip()


def run_once(dictionary, directory=".", timeout=170):
    """Run the benchmark once. Returns (check_seconds, load_seconds, misspelled)."""
    result = subprocess.run(
        f"./speller_bench bench/{dictionary} bench/text",
        shell=True, cwd=directory, capture_output=True, text=True, timeout=timeout)

    check = re.search(r"BENCH CHECK ([0-9.]+)", result.stdout)
    load = re.search(r"BENCH LOAD ([0-9.]+)", result.stdout)
    misspelled = re.search(r"WORDS MISSPELLED:\s+(\d+)", result.stdout)

    if not (check and load and misspelled):
        raise RuntimeError(f"benchmark produced no numbers: {result.stdout[-300:]}")

    return float(check.group(1)), float(load.group(1)), int(misspelled.group(1))


def measure(directory="."):
    """Time lookups against the small and the large dictionary.

    Runs one pair first; only if that looks bad does it repeat, so a correct
    submission costs about a second. Returns a dict of results.
    """
    small, load_small, missed_small = run_once("small", directory)
    large, load_large, missed_large = run_once("large", directory)

    samples_small = [small]
    samples_large = [large]

    ratio = large / small if small > 0 else float("inf")

    # Repeat only when the first pair looks slow, and not at all when the run
    # is already so slow that repeating would risk the check's own timeout
    if ratio > 10 and (load_large + large) < 15:
        for _ in range(2):
            samples_small.append(run_once("small", directory)[0])
            samples_large.append(run_once("large", directory)[0])

    small = sorted(samples_small)[len(samples_small) // 2]
    large = sorted(samples_large)[len(samples_large) // 2]

    return {
        "small": small,
        "large": large,
        "ratio": large / small if small > 0 else float("inf"),
        "load_large": load_large,
        "misspelled": missed_small + missed_large,
        "runs": len(samples_small),
    }
