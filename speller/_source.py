"""Look for evidence of a hash table (or a trie) in a student's C source.

This is deliberately a heuristic: it can be fooled, and it is only ever used to
log a note for a human grader, never to fail a student. See data_structure() in
__init__.py.
"""

import os
import re

# Files that belong to the check itself, not to the student
SKIP = {"speller.c", "speller_bench.c"}


def strip_c(source):
    """Blank out comments and string/character literals.

    Whitespace and newlines are preserved, so line numbers still match the
    original file. Stripping matters a great deal here: every submission
    contains printf("%s\\n", word), and that % would otherwise look like the
    modulo of a hash function.
    """
    out = []
    i = 0
    n = len(source)
    state = "code"

    while i < n:
        c = source[i]
        following = source[i + 1] if i + 1 < n else ""

        if state == "code":
            if c == "/" and following == "/":
                state = "line"
                i += 2
                continue
            if c == "/" and following == "*":
                state = "block"
                out.append("  ")
                i += 2
                continue
            if c == '"':
                state = "string"
                out.append(" ")
                i += 1
                continue
            if c == "'":
                state = "char"
                out.append(" ")
                i += 1
                continue
            out.append(c)
            i += 1
            continue

        if state == "line":
            if c == "\n":
                state = "code"
                out.append("\n")
            else:
                out.append(" ")
            i += 1
            continue

        if state == "block":
            if c == "*" and following == "/":
                state = "code"
                out.append("  ")
                i += 2
                continue
            out.append("\n" if c == "\n" else " ")
            i += 1
            continue

        # inside a string or character literal
        if c == "\\" and i + 1 < n:
            out.append("\n" if following == "\n" else " ")
            out.append(" ")
            i += 2
            continue
        if (state == "string" and c == '"') or (state == "char" and c == "'"):
            state = "code"
            out.append(" ")
            i += 1
            continue
        out.append("\n" if c == "\n" else " ")
        i += 1

    return "".join(out)


def student_sources(directory="."):
    """Every top-level .c/.h the student handed in, minus the check's own files.

    Not just dictionary.c: students may split the table off into hashtable.c,
    and scanning one file would flag exactly the students who organised their
    code best.
    """
    return [name for name in sorted(os.listdir(directory))
            if name.endswith((".c", ".h"))
            and name not in SKIP
            and os.path.isfile(os.path.join(directory, name))]


def _file_scope_arrays(code):
    """Names of arrays declared outside any function, with size >= 2."""
    found = []
    depth = 0
    for line in code.split("\n"):
        if depth == 0:
            match = re.search(
                r"(?:struct\s+\w+|\w+)\s*\*+\s*(\w+)\s*\[\s*(\w+)\s*\]"     # node *table[N]
                r"|(?:struct\s+\w+|\w+)\s+(\w+)\s*\[\s*(\w+)\s*\]",         # node table[N]
                line)
            if match and "(" not in line:
                size = match.group(2) or match.group(4)
                # a named constant counts; a number has to be at least 2
                if not size.isdigit() or int(size) >= 2:
                    found.append(match.group(1) or match.group(3))
        depth += line.count("{") - line.count("}")
    return found


def hash_signals(code):
    """Which hash-table hallmarks fire on this (already stripped) source."""
    hits = set()

    # H1: the vocabulary of hashing
    if re.search(r"(?i)\b(hash|djb2?|sdbm|fnv|murmur|jenkins|crc32|bucket)\w*", code):
        hits.add("hash-function name")

    # H2: reducing a number to a table index. A bare & is address-of, so only
    # the power-of-two mask idiom counts.
    if (re.search(r"%\s*[A-Za-z_]\w*", code)
            or re.search(r"%\s*\d+", code)
            or re.search(r"&\s*\(?\s*[A-Za-z_]\w*\s*-\s*1\s*\)?", code)):
        hits.add("modulo reduction")

    # H3: a loop over the characters of a word, accumulating into a number.
    # This is what catches a hash computed inline, with no function called hash.
    for match in re.finditer(r"\b(?:for|while)\s*\(([^)]*)\)", code):
        header = match.group(1)
        if not re.search(r"\\0|strlen|\[\s*\w+\s*\]|\*\s*\w+\+\+", header):
            continue
        body = code[match.end():match.end() + 400]
        if re.search(r"[+*^|]=|<<", body):
            hits.add("character-accumulating loop")
            break

    # H4: a table living at file scope
    arrays = _file_scope_arrays(code)
    if arrays:
        hits.add("file-scope table")

    # H5: indexing something by a computed value. Subscripts containing - '
    # are excluded: [c - 'a'] is the trie idiom, not a hash.
    for match in re.finditer(r"\w+\s*\[([^\]\[]*)\]", code):
        index = match.group(1)
        if "- '" in index or "-'" in index:
            continue
        if re.search(r"(?i)\bhash\w*\s*\(|\b(hash\w*|index|idx|bucket\w*|key)\b", index):
            hits.add("computed subscript")
            break

    return hits


def trie_signals(code):
    """Which trie hallmarks fire on this (already stripped) source."""
    hits = set()

    # T1 is decisive: a node holding an ARRAY of pointers to its own type.
    # A chained hash table's node holds a single self-pointer (node *next),
    # never an array of them.
    for match in re.finditer(
            r"(?:typedef\s+)?struct\s+(\w+)?\s*\{(.*?)\}\s*(\w*)\s*;", code, re.S):
        tag, body, alias = match.group(1), match.group(2), match.group(3)
        names = {name for name in (tag, alias) if name}
        for member in re.finditer(r"(?:struct\s+)?(\w+)\s*\*+\s*\w+\s*\[", body):
            if member.group(1) in names:
                hits.add("node with an array of pointers to itself")

    # T2: the vocabulary of tries
    if re.search(r"(?i)\b(trie|children|child)\w*", code):
        hits.add("trie vocabulary")

    # T3: indexing by a letter's position in the alphabet
    if re.search(r"\[[^\]\[]*-\s*'[aA]'[^\]\[]*\]", code):
        hits.add("alphabet-offset indexing")

    # T4: a single root, and no table to speak of
    if re.search(r"^\s*(?:static\s+)?(?:struct\s+)?\w+\s*\*\s*root\b", code, re.M) \
            and not _file_scope_arrays(code):
        hits.add("single root pointer")

    return hits


def classify(directory="."):
    """Decide what the student's data structure looks like.

    Returns (verdict, hash_hits, trie_hits, scanned) where verdict is one of
    "hash", "trie", "both" or "unknown".
    """
    scanned = student_sources(directory)

    code = ""
    for name in scanned:
        with open(os.path.join(directory, name), errors="replace") as f:
            code += strip_c(f.read()) + "\n"

    hash_hits = hash_signals(code)
    trie_hits = trie_signals(code)

    named = "hash-function name" in hash_hits
    reduces = "modulo reduction" in hash_hits
    table = "file-scope table" in hash_hits
    accumulates = "character-accumulating loop" in hash_hits
    subscript = "computed subscript" in hash_hits

    is_hash = ((named and reduces)
               or (reduces and table and (accumulates or subscript))
               or len(hash_hits) >= 3)

    is_trie = ("node with an array of pointers to itself" in trie_hits
               or len(trie_hits) >= 2)

    if is_hash and is_trie:
        verdict = "both"
    elif is_hash:
        verdict = "hash"
    elif is_trie:
        verdict = "trie"
    else:
        verdict = "unknown"

    return verdict, hash_hits, trie_hits, scanned
