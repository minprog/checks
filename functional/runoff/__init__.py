"""Checks for "Runoff zonder loops".

The student rewrites the functions of their Runoff solution without loops, using
their own map, filter and reduce, which they paste into a
marked region of runoff.c.

* The behaviour is checked by the checks of the original Runoff assignment,
  reused as they are (testing.c next to this file is a copy of ../../runoff/testing.c).
* On top of that: the eight functions may not contain a loop, and between them
  they use all three of map, filter and reduce.
* reset_votes and print_tied_candidates are new, they replace loops of the old main.
* A few complete elections run end to end.
"""

import re

import check50
import check50.c
import check50.internal

common = check50.internal.import_file(
    "common",
    check50.internal.check_dir / "../_common.py"
)

# Importing registers the checks of the original assignment as checks of this one
original = check50.internal.import_file(
    "runoff_original",
    check50.internal.check_dir / "../../runoff/__init__.py"
)

# check50 only runs the checks that are members of this module
def _reexport():
    for name, member in list(vars(original).items()):
        if hasattr(member, "_check_dependency"):
            globals()[name] = member


_reexport()

FILE = "runoff.c"
FLAGS = {"lcs50": True}

FUNCTIONS = ["vote", "tabulate", "print_winner", "find_min", "is_tie", "eliminate",
             "reset_votes", "print_tied_candidates"]
TOOLS = ["map", "filter", "reduce"]


def bodies():
    source = common.read_source(FILE)
    return {name: common.function_body(source, name, FILE) for name in FUNCTIONS}


# ---------------------------------------------------------------- how it is written

@check50.check(original.exists)
def has_markers():
    """runoff.c still has the marked region for map, filter and reduce"""
    with open(FILE) as f:
        source = f.read()
    begin = re.search(r"//\s*-+\s*BEGIN:", source)
    end = re.search(r"//\s*-+\s*END\s*-+", source)
    if begin is None or end is None or begin.start() > end.start():
        raise check50.Failure("could not find the markers around the pasted map, filter and reduce",
                              help="Keep the lines '// ---- BEGIN: map, filter, reduce ----' and "
                                   "'// ---- END ----' of the template, and put your three functions between them.")


@check50.check(original.exists)
def no_loops():
    """vote, tabulate, print_winner, find_min, is_tie, eliminate, reset_votes and print_tied_candidates have no loops"""
    for name, body in bodies().items():
        loop = re.search(r"\b(for|while|do|goto)\b", body)
        if loop:
            raise check50.Failure(f"{name} contains a loop ({loop.group(1)})",
                                  help="Repetition has to come from map, filter and reduce. "
                                       "A loop in the functions of main does not count: only these eight functions are checked.")


def uses(tool):
    if not any(re.search(rf"\b{tool}\s*\(", body) for body in bodies().values()):
        raise check50.Failure(f"none of the eight functions calls {tool}",
                              help=f"This assignment is about using your own {tool}.")


@check50.check(original.exists)
def uses_map():
    """map is used"""
    uses("map")


@check50.check(original.exists)
def uses_filter():
    """filter is used"""
    uses("filter")


@check50.check(original.exists)
def uses_reduce():
    """reduce is used"""
    uses("reduce")


# ---------------------------------------------------------------- the two new functions

SETUP = r"""
static void t_setup(const char *names[], int n)
{
    candidate_count = n;
    for (int i = 0; i < n; i++)
    {
        candidates[i].name = (string) names[i];
        candidates[i].votes = 0;
        candidates[i].eliminated = false;
    }
}
"""


@check50.check(original.compiles)
def reset_votes_works():
    """reset_votes sets the votes of all candidates back to zero"""
    common.run_test(FILE, SETUP + r"""
int main(void)
{
    const char *names[] = {"Alice", "Bob", "Charlie", "David"};
    int votes[] = {3, 5, 0, 7};
    t_setup(names, 4);
    for (int i = 0; i < 4; i++)
    {
        candidates[i].votes = votes[i];
    }
    candidates[2].eliminated = true;
    reset_votes();
    for (int i = 0; i < 4; i++)
    {
        EXPECT(candidates[i].votes == 0, "after reset_votes the votes of %s are %d, expected 0", names[i], candidates[i].votes);
    }
}
""", flags=FLAGS)


def tied_output(eliminated, names):
    main = SETUP + r"""
int main(void)
{
    const char *names[] = {%s};
    t_setup(names, %d);
    %s
    print_tied_candidates();
}
""" % (", ".join(f'"{name}"' for name in names), len(names),
       " ".join(f"candidates[{i}].eliminated = true;" for i in eliminated))
    return common.run_capture(FILE, main, flags=FLAGS)


def expect_names(output, expected, situation):
    got = [line.strip() for line in output.splitlines() if line.strip()]
    if got != expected:
        raise check50.Failure(f"{situation}: expected {expected} but found {got}",
                              help="print_tied_candidates prints the names of the candidates that are not eliminated, "
                                   "one per line, in the order of the candidates.")


@check50.check(original.compiles)
def print_tied_candidates_all():
    """print_tied_candidates prints all candidates when nobody is eliminated"""
    expect_names(tied_output([], ["Alice", "Bob", "Charlie"]),
                 ["Alice", "Bob", "Charlie"], "no candidates eliminated")


@check50.check(original.compiles)
def print_tied_candidates_skips_eliminated():
    """print_tied_candidates skips eliminated candidates and keeps the order"""
    expect_names(tied_output([1, 3], ["Alice", "Bob", "Charlie", "David", "Eve"]),
                 ["Alice", "Charlie", "Eve"], "Bob and David eliminated")


@check50.check(original.compiles)
def print_tied_candidates_one_left():
    """print_tied_candidates prints one name when one candidate is left"""
    expect_names(tied_output([0, 1], ["Alice", "Bob", "Charlie"]),
                 ["Charlie"], "Alice and Bob eliminated")


# ---------------------------------------------------------------- whole elections

def election(candidates, ballots):
    """Run ./runoff with the given ballots (a list of lists of names), return what it printed without the prompts"""
    lines = [str(len(ballots))] + [name for ballot in ballots for name in ballot]
    with open("ballots.txt", "w") as f:
        f.write("\n".join(lines) + "\n")

    output = check50.run(f"./runoff {' '.join(candidates)} < ballots.txt").stdout()
    output = re.sub(r"(Number of voters|Rank \d+): ", "", output)
    return [line.strip() for line in output.splitlines() if line.strip()]


def expect_election(candidates, ballots, expected, situation):
    got = election(candidates, ballots)
    if got != expected:
        raise check50.Failure(f"{situation}: expected {expected} but found {got}",
                              help=f"Ran ./runoff {' '.join(candidates)} with these ballots:\n"
                                   + "\n".join(" > ".join(ballot) for ballot in ballots))


@check50.check(original.compiles)
def election_majority():
    """an election with a majority in the first round: Alice wins"""
    expect_election(["Alice", "Bob", "Charlie"],
                    [["Alice", "Bob", "Charlie"], ["Alice", "Charlie", "Bob"], ["Bob", "Alice", "Charlie"]],
                    ["Alice"], "election with a majority in the first round")


@check50.check(original.compiles)
def election_runoff_round():
    """an election that needs a runoff round: Bob wins after Charlie is eliminated"""
    expect_election(["Alice", "Bob", "Charlie"],
                    [["Alice", "Bob", "Charlie"], ["Alice", "Charlie", "Bob"], ["Bob", "Alice", "Charlie"],
                     ["Bob", "Charlie", "Alice"], ["Charlie", "Bob", "Alice"]],
                    ["Bob"], "election that needs a runoff round")


@check50.check(original.compiles)
def election_tie():
    """an election that ends in a tie between two candidates prints both"""
    expect_election(["Alice", "Bob"], [["Alice", "Bob"], ["Bob", "Alice"]],
                    ["Alice", "Bob"], "tie between two candidates")


@check50.check(original.compiles)
def election_tie_after_elimination():
    """an election that ends in a tie between Alice and Bob after Charlie and David are eliminated"""
    expect_election(["Alice", "Bob", "Charlie", "David"],
                    [["Alice", "Bob", "Charlie", "David"], ["Alice", "Bob", "Charlie", "David"],
                     ["Bob", "Alice", "Charlie", "David"], ["Bob", "Alice", "Charlie", "David"],
                     ["Charlie", "Alice", "Bob", "David"], ["David", "Bob", "Alice", "Charlie"]],
                    ["Alice", "Bob"], "tie after two eliminations")


@check50.check(original.compiles)
def election_three_way_tie():
    """an election that ends in a three-way tie prints all three"""
    expect_election(["Alice", "Bob", "Charlie"],
                    [["Alice", "Bob", "Charlie"], ["Bob", "Charlie", "Alice"], ["Charlie", "Alice", "Bob"]],
                    ["Alice", "Bob", "Charlie"], "three-way tie")


@check50.check(original.compiles)
def election_invalid_vote():
    """an invalid vote is reported with exit code 4"""
    with open("ballots.txt", "w") as f:
        f.write("1\nAlice\nZed\n")
    check50.run("./runoff Alice Bob < ballots.txt").stdout("Invalid vote.").exit(4)
