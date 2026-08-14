import check50
import check50.c
import os

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)
helpers.set_stdout_limit(1000)

bench = check50.internal.import_file(
    "bench", check50.internal.check_dir / "_bench.py")
source = check50.internal.import_file(
    "source", check50.internal.check_dir / "_source.py")

# A lookup may not take more than RATIO times as long when the dictionary grows
# 50x, AND may not take more than SECONDS of CPU time in total. Both have to be
# exceeded before anything fails: a hash table with very few buckets grows just
# as steeply as a linked list, but stays far below the absolute limit, and the
# assignment leaves the number of buckets entirely up to the student.
SCALING_RATIO = 20.0
SCALING_SECONDS = 0.8

@check50.check()
def exists():
    """dictionary.c, dictionary.h, and Makefile exist"""
    check50.exists("dictionary.c", "dictionary.h")

@check50.check(exists)
def compiles():
    """speller compiles"""
    check50.include("speller.c")
    if not os.path.exists("Makefile"):
        check50.include("Makefile")
    check50.run("make").exit(0)


@check50.check(compiles)
def basic():
    """handles most basic words properly"""
    check50.include("basic")
    check50.run("./speller basic/dict basic/text").stdout(open("basic/out")).exit(0)


@check50.check(compiles)
def min_length():
    """handles min length (1-char) words"""
    check50.include("min_length")
    check50.run("./speller min_length/dict min_length/text").stdout(open("min_length/out")).exit(0)


@check50.check(compiles)
def max_length():
    """handles max length (45-char) words"""
    check50.include("max_length")
    check50.run("./speller max_length/dict max_length/text").stdout(open("max_length/out")).exit(0)


@check50.check(compiles)
def apostrophe():
    """handles words with apostrophes properly"""
    check50.include("apostrophe")
    check50.run("./speller apostrophe/without/dict apostrophe/with/text").stdout(open("apostrophe/outs/without-with")).exit(0)
    check50.run("./speller apostrophe/with/dict apostrophe/without/text").stdout(open("apostrophe/outs/with-without")).exit(0)
    check50.run("./speller apostrophe/with/dict apostrophe/with/text").stdout(open("apostrophe/outs/with-with")).exit(0)


@check50.check(compiles)
def case():
    """spell-checking is case-insensitive"""
    check50.include("case")
    check50.run("./speller case/dict case/text").stdout(open("case/out")).exit(0)


@check50.check(compiles)
def substring():
    """handles substrings properly"""
    check50.include("substring")
    check50.run("./speller substring/dict substring/text").stdout(open("substring/out")).exit(0)


@check50.check(substring)
def memory():
    """program is free of memory errors"""
    check50.c.valgrind("./speller substring/dict substring/text").stdout(open("substring/out"), timeout=10).exit(0)


@check50.check(compiles, timeout=180)
def scaling():
    """looking up a word does not get slower as the dictionary grows"""
    check50.include("speller_bench.c")
    bench.generate("bench")

    # The student's own Makefile has no target for our benchmark, so build it
    # ourselves from all of their sources. If that does not work out, say so
    # and pass: an unusual build is no evidence about the data structure.
    built, command, output = bench.build()
    if not built:
        check50.log("could not build the benchmark, so lookups were not timed")
        check50.log(f"    {command}")
        check50.log(f"    {output.splitlines()[0] if output else ''}")
        return

    try:
        result = bench.measure()
    except Exception as error:
        check50.log(f"could not time lookups: {error}")
        return

    # Every word of the text is in both dictionaries, so anything else means we
    # are not measuring successful lookups. Correctness is checked elsewhere.
    if result["misspelled"] != 0:
        check50.log("the benchmark found misspelled words where there are none, "
                    "so lookups were not timed")
        return

    check50.data(check_small=result["small"], check_large=result["large"],
                 ratio=result["ratio"], runs=result["runs"])
    check50.log(f"{bench.N_LOOKUPS} lookups took {result['small']:.3f}s with "
                f"{bench.N_SMALL} words and {result['large']:.3f}s with "
                f"{bench.N_LARGE} words")

    if result["ratio"] > SCALING_RATIO and result["large"] > SCALING_SECONDS:
        raise check50.Failure(
            f"looking up a word takes {result['ratio']:.0f} times as long when "
            f"the dictionary is {bench.STRIDE} times bigger",
            help=(f"Looking up {bench.N_LOOKUPS} words took "
                  f"{result['small']:.3f} seconds with a dictionary of "
                  f"{bench.N_SMALL} words, but {result['large']:.3f} seconds "
                  f"with a dictionary of {bench.N_LARGE} words. In a hash table "
                  "a lookup only has to search one bucket, so a bigger "
                  "dictionary should not make lookups much slower. This looks "
                  "like every lookup walks a large part of the whole dictionary."))


@check50.check(exists)
def data_structure():
    """checked which data structure dictionary.c uses"""
    # Note: this check always passes. Recognising a data structure from source
    # code is guesswork, so a student is never blocked by it; it only leaves a
    # note for whoever reads the submission.
    verdict, hash_hits, trie_hits, scanned = source.classify()

    check50.data(structure=verdict, hash_signals=sorted(hash_hits),
                 trie_signals=sorted(trie_hits), scanned=scanned)

    if verdict == "hash":
        check50.log("looks like a hash table")
    elif verdict == "trie":
        check50.log("this looks like a trie, not a hash table. A trie is the "
                    "Speller Challenge; this assignment asks for a hash table.")
        check50.log("flagged for a human to look at")
    elif verdict == "both":
        check50.log("found signs of both a hash table and a trie")
        check50.log("flagged for a human to look at")
    else:
        check50.log("could not tell from the source whether this is a hash "
                    "table. That is not an error and this check passes.")
        check50.log("flagged for a human to look at")

    if hash_hits:
        check50.log(f"    hash table: {', '.join(sorted(hash_hits))}")
    if trie_hits:
        check50.log(f"    trie: {', '.join(sorted(trie_hits))}")
