import contextlib
import check50
import re
import string

__all__ = ["replace_main", "ascii_art_regex", "side_by_side", "expect_ascii_art"]


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


def side_by_side(expected: str, actual: str) -> str:
    """Render expected and actual output next to each other, line by line."""
    expected_lines = expected.splitlines()
    actual_lines = [line.rstrip() for line in actual.replace("\r\n", "\n").splitlines()]

    header_expected, header_actual = "verwacht:", "jouw uitvoer:"
    width = max([len(line) for line in expected_lines] + [len(header_expected)])

    lines = [
        f"{header_expected.ljust(width)}   {header_actual}",
        f"{'-' * width}   {'-' * len(header_actual)}"
    ]

    for i in range(max(len(expected_lines), len(actual_lines))):
        left = expected_lines[i] if i < len(expected_lines) else ""
        right = actual_lines[i] if i < len(actual_lines) else ""
        marker = "  " if left == right else "<>"
        lines.append(f"{left.ljust(width)} {marker}{right}")

    return "\n".join(lines)


def expect_ascii_art(process, expected: str, rationale: str = "de uitvoer is niet zoals verwacht"):
    """Expect expected as output of process, reporting any mismatch side by side."""
    try:
        process.stdout(ascii_art_regex(expected), str_output=expected)
    except check50.Mismatch as error:
        actual = error.payload["actual"]
    except check50.Missing as error:
        actual = error.payload["collection"]
    else:
        return process

    raise check50.Failure(rationale, help=side_by_side(expected, actual))
