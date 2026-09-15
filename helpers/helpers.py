import contextlib
import check50
import re
import string

__all__ = ["replace_main", "ascii_art_regex", "side_by_side", "only_whitespace_differs", "first_difference", "expect_ascii_art", "has_function"]


def set_stdout_limit(char_limit: int):
    from pexpect.exceptions import EOF
    import check50._api

    def _raw(s):
        """Get raw representation of s, truncating if too long."""

        if isinstance(s, list):
            s = "\n".join(_raw(item) for item in s)

        if s == EOF:
            return "EOF"

        s = f'"{repr(str(s))[1:-1]}"'
        if len(s) > char_limit:
            s = s[:char_limit] + "...\""  # Truncate if too long
        return s

    check50._api._raw = _raw

@contextlib.contextmanager
def replace_main(filename: str, main: str, show_main_in_help=True) -> tuple[None, None, None]:
    """replace or insert main into file"""
    main = "\n" + main + "\n"

    with open(filename) as f:
        content = f.read()

    indices = find_main(content)
    if indices:
        start, end = indices
        # always append main to eof instead of in-place. This way
        # a commented out main does not stay commented out after replacing
        new_content = content[:start] + "\n" + content[end + 1:] + main
    else:
        new_content = content + main

    try:
        with open(filename, "w") as f:
            f.write(new_content)
        yield
    except check50.Failure as e:
        with open(filename, "w") as f:
            f.write(content)
        if show_main_in_help:
            msg = f"The following main function was used to test your code:\n{main}"
            if "help" in e.payload and e.payload["help"] is not None:
                e.payload["help"] += "\n" + msg
            else:
                e.payload["help"] = msg
        raise e
    except Exception as e:
        with open(filename, "w") as f:
            f.write(content)
        raise e

def has_function(content: str, name: str) -> bool:
    """Whether a function called name appears in content, allowing whitespace before the ("""
    return re.search(rf"\b{re.escape(name)}\s*\(", content) is not None

def find_main(content: str) -> tuple[int, int] | None:
    match = re.compile(r"int\s+main\s*\(", re.MULTILINE).search(content)
    if match:
        index = match.start()
        index_closing_bracket = find_closing_bracket(content[index:])
        return (index, index + index_closing_bracket)
    return None

def find_closing_bracket(content: str) -> int:
    n_open_brackets = -1
    for i, char in enumerate(content):
        # No brackets, but statement is closed through ;
        if char == ";" and n_open_brackets == -1:
            return i

        if char == "{":
            if n_open_brackets == -1:
                n_open_brackets = 1
            else:
                n_open_brackets += 1

        if char == "}":
            n_open_brackets -= 1

        if n_open_brackets == 0:
            return i

    return -1

def encode_unprintable(s: str) -> str:
    encoded_string = ""
    for char in s:
        # note: str.isprintable() has a different definition of printable :(
        if char in string.printable:
            encoded_string += char
        else:
            encoded_string += "\\x{:02x}".format(ord(char))
    return encoded_string


def ascii_art_regex(expected: str) -> str:
    """Turn ASCII art into a regex that ignores trailing whitespace per line.

    A trailing newline is only required if expected ends with one.
    """
    lines = expected.splitlines()
    regex = r"\s*\n".join(re.escape(line) for line in lines) + r"\s*"
    if expected.endswith("\n"):
        regex += "\n"
    return regex


def side_by_side(expected: str, actual: str, max_extra_lines: int = 5) -> str:
    """Render expected and actual output next to each other, line by line.

    At most max_extra_lines lines beyond the expected output are shown, so
    that runaway output (e.g. from an infinite loop) stays readable.
    """
    expected_lines = expected.splitlines()
    actual_lines = _lines(actual)

    header_expected, header_actual = "verwacht:", "jouw uitvoer:"
    width = max([len(line) for line in expected_lines] + [len(header_expected)])

    lines = [
        f"{header_expected.ljust(width)}   {header_actual}",
        f"{'-' * width}   {'-' * len(header_actual)}"
    ]

    n_rows = min(max(len(expected_lines), len(actual_lines)), len(expected_lines) + max_extra_lines)
    for i in range(n_rows):
        left = expected_lines[i] if i < len(expected_lines) else ""
        right = actual_lines[i] if i < len(actual_lines) else ""
        marker = "  " if left == right else "<>"
        lines.append(f"{left.ljust(width)} {marker}{right}")

    n_hidden = len(actual_lines) - n_rows
    if n_hidden > 0:
        lines.append(f"{''.ljust(width)}   ... en nog {n_hidden} regels")

    return "\n".join(lines)


def only_whitespace_differs(expected: str, actual: str) -> bool:
    """Whether expected and actual are the same when ignoring all whitespace within lines and blank lines."""
    def visible(text):
        return ["".join(line.split()) for line in _lines(text) if line.strip()]

    return expected != actual and visible(expected) == visible(actual)


def expect_ascii_art(process, expected: str, rationale: str = "de uitvoer is niet zoals verwacht",
                     max_extra_lines: int = 5):
    """Expect expected as output of process, reporting any mismatch side by side."""
    try:
        process.stdout(ascii_art_regex(expected), str_output=expected)
    except check50.Mismatch as error:
        actual = error.payload["actual"]
    except check50.Missing as error:
        actual = error.payload["collection"]
    else:
        return process

    hint = ""
    too_long = actual.count("\n") > len(expected.splitlines()) + max_extra_lines

    if only_whitespace_differs(expected, actual):
        hint = "alle tekens kloppen, het verschil zit in de witruimte: kijk goed naar spaties en lege regels\n"

    # timed out while still running and printing far more than expected: likely an infinite loop
    elif too_long and process.process.isalive():
        hint = "je programma lijkt niet te stoppen en blijft uitvoer geven, zit er misschien een oneindige loop in?\n"

    # check50 indents only the first line of help, so start the table on a line of its own
    help = hint + "\n" + side_by_side(expected, actual, max_extra_lines)

    difference = first_difference(expected, actual)
    if difference:
        row, column = difference
        expected_lines, actual_lines = expected.splitlines(), _lines(actual)
        expected_line = expected_lines[row] if row < len(expected_lines) else ""
        actual_line = actual_lines[row] if row < len(actual_lines) else ""
        help += (f"\n\neerste verschil in regel {row + 1}, bij teken {column + 1}:\n"
                 f"verwacht:      \"{expected_line}\"\n"
                 f"jouw uitvoer:  \"{actual_line}\"")

    raise check50.Failure(rationale, help=help)


def first_difference(expected: str, actual: str) -> tuple[int, int] | None:
    """Return (line, column) of the first difference between expected and actual, ignoring trailing whitespace."""
    expected_lines, actual_lines = expected.splitlines(), _lines(actual)

    for row in range(max(len(expected_lines), len(actual_lines))):
        left = expected_lines[row] if row < len(expected_lines) else ""
        right = actual_lines[row] if row < len(actual_lines) else ""
        if left != right:
            return row, _first_difference(left, right)

    return None


def _lines(text: str) -> list[str]:
    """Split output into lines without trailing whitespace."""
    return [line.rstrip() for line in text.replace("\r\n", "\n").splitlines()]


def _first_difference(left: str, right: str) -> int:
    """Index of the first character where left and right differ."""
    for i, (a, b) in enumerate(zip(left, right)):
        if a != b:
            return i
    return min(len(left), len(right))
