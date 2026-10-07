"""Shared machinery for the functional programming checks.

The student submits a file with only some functions (and maybe a main of their
own). Every check replaces that main with a test program of its own. Such a
test program prints nothing when everything is fine. When something is wrong,
it prints a single line describing what and exits with a non-zero code. This
module turns that into a check50 result.
"""

import functools
import os
import re
import subprocess
import tempfile

import check50
import check50.c
import check50.internal

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../../helpers/helpers.py"
)
helpers.set_stdout_limit(2000)

# Prepended to every test main
PRELUDE = r"""
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stddef.h>

#define EXPECT(cond, ...) \
    do { if (!(cond)) { printf(__VA_ARGS__); printf("\n"); exit(1); } } while (0)

static void t_fmt_ints(char *buf, size_t cap, const int *a, int n)
{
    size_t used = 0;
    buf[0] = '\0';
    for (int i = 0; i < n && used + 16 < cap; i++)
    {
        used += snprintf(buf + used, cap - used, "%s%d", i ? ", " : "", a[i]);
    }
}

// Fails unless got[0..n) equals want[0..n)
static void t_expect_ints(const char *what, const int *got, const int *want, int n)
{
    for (int i = 0; i < n; i++)
    {
        if (got[i] != want[i])
        {
            char g[256], w[256];
            t_fmt_ints(g, sizeof(g), got, n);
            t_fmt_ints(w, sizeof(w), want, n);
            printf("%s: expected {%s} but found {%s}\n", what, w, g);
            exit(1);
        }
    }
}
"""


@functools.lru_cache(maxsize=None)
def asan_works():
    """Whether programs compiled with the address sanitizer run in this environment"""
    with tempfile.TemporaryDirectory() as directory:
        source = os.path.join(directory, "probe.c")
        exe = os.path.join(directory, "probe")
        with open(source, "w") as f:
            f.write("int main(void) { return 0; }\n")
        try:
            subprocess.run(["clang", "-fsanitize=address", source, "-o", exe],
                           check=True, capture_output=True, timeout=60)
            subprocess.run([exe], check=True, capture_output=True, timeout=30,
                           env={**os.environ, "ASAN_OPTIONS": "detect_leaks=0"})
        except (subprocess.SubprocessError, OSError):
            return False
    return True


def _execute(filename, main, asan, timeout, flags):
    """Compile filename with the given main in place of the student's own, run it: (output, exit code)"""
    exe = filename[:-2]
    compile_flags = dict(flags or {})
    if asan and asan_works():
        compile_flags["fsanitize"] = "address"

    with helpers.replace_main(filename, PRELUDE + "\n" + main):
        check50.c.compile(filename, **compile_flags)
        process = check50.run(f"./{exe}", env={"ASAN_OPTIONS": "detect_leaks=0"})
        output = process.stdout(timeout=timeout)
        return output, process.exitcode


def run_test(filename, main, *, asan=True, timeout=5, flags=None):
    """Run a test program in place of the student's main, which prints nothing when all is well.

    asan: compile with the address sanitizer, so reading or writing outside of
    an array becomes a clear failure instead of silent garbage. Leave it off
    for tests that measure speed.
    flags: extra compile flags, for example {"lcs50": True}
    """
    output, code = _execute(filename, main, asan, timeout, flags)
    _judge(filename, output, code)


def run_capture(filename, main, *, asan=True, timeout=5, flags=None):
    """Like run_test, but returns what the test program printed, for the caller to judge"""
    output, code = _execute(filename, main, asan, timeout, flags)
    _check_crash(filename, output, code)
    return output


def _check_crash(filename, output, code):
    """Fail if the address sanitizer complained or the program died without a word"""
    if "AddressSanitizer" in output:
        kind = re.search(r"AddressSanitizer: ([\w-]+)", output)
        where = re.search(rf"#\d+ 0x\w+ in (\w+) .*?({re.escape(filename)}:\d+)", output)
        message = "your code accesses memory it should not"
        if kind:
            message += f" ({kind.group(1)})"
        if where:
            message += f", in {where.group(1)} at {where.group(2)}"
        raise check50.Failure(message, help="\n".join(output.splitlines()[:12]))

    if code != 0:
        raise check50.Failure(f"the test program crashed (exit code {code})")


def _judge(filename, output, code):
    if "AddressSanitizer" in output:
        _check_crash(filename, output, code)

    lines = [line for line in output.splitlines() if line.strip()]
    if lines:
        raise check50.Failure(lines[0], help="\n".join(lines[1:]) or None)

    _check_crash(filename, output, code)


def no_malloc(filename):
    with open(filename) as f:
        for number, line in enumerate(f, 1):
            if "malloc" in line or "calloc" in line or "realloc" in line:
                raise check50.Failure(
                    f"found dynamic memory allocation on line {number}: {line.strip()}",
                    help="This assignment can be done in place, without extra memory.")


def read_source(filename):
    """The contents of filename, without comments and with string literals emptied"""
    with open(filename) as f:
        source = f.read()
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    source = re.sub(r"//[^\n]*", "", source)
    return re.sub(r'"(\\.|[^"\\])*"', '""', source)


def function_body(source, name, filename):
    """The text between the braces of the definition of function name, or a Failure"""
    match = re.search(rf"\b{name}\s*\([^;{{}}]*\)\s*\{{", source)
    if match is None:
        raise check50.Failure(f"could not find a function {name} in {filename}",
                              help=f"The assignment asks for a function called {name}.")
    start = match.end() - 1
    end = start + helpers.find_closing_bracket(source[start:])
    return source[start + 1:end]
