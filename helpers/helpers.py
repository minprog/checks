import contextlib

__all__ = ["replace_main"]

@contextlib.contextmanager
def replace_main(filename: str, main: str) -> tuple[None, None, None]:
    """replace or insert main into file"""
    main = "\n" + main + "\n"

    with open(filename) as f:
        content = f.read()

    indices = find_main(content)
    if indices:
        start, end = indices
        new_content = content[:start] + main + content[end + 1:]
    else:
        new_content += main

    try:
        with open(filename, "w") as f:
            f.write(new_content)
        yield
    except Exception as e:
        with open(filename, "w") as f:
            f.write(content)
        raise e

def find_main(content: str) -> tuple[int, int] | None:
    index = content.find("int main(")
    if index != -1:
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