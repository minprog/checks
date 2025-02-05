import check50
import check50.c
import check50.internal

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)
helpers.set_stdout_limit(10000)


@check50.check()
def exists():
    """graph.c exists"""
    check50.exists("graph.c")

@check50.check(exists)
def compiles():
    """graph.c compiles"""
    check50.c.compile("graph.c", lcs50=True)

@check50.check(compiles)
def test_graph_0_1_0():
    """graph voor f(x) = 0 * x^2 + 1 * x + 0 is correct"""
    graph = check50.run("./graph").stdin("0").stdin("1").stdin("0").stdout()
    assert_graph(graph, "0_1_0.txt")

@check50.check(compiles)
def test_graph_0005_0_0():
    """graph voor f(x) = 0.005 * x^2 + 0 * x + 0 is correct"""
    graph = check50.run("./graph").stdin("0.005").stdin("0").stdin("0").stdout()
    assert_graph(graph, "0005_0_0.txt")

@check50.check(compiles)
def test_graph_001_0_20():
    """graph voor f(x) = -0.01 * x^2 + 0 * x + 20 is correct"""
    graph = check50.run("./graph").stdin("-0.01").stdin("0").stdin("20").stdout()
    assert_graph(graph, "001_0_20.txt")

@check50.check(compiles)
def test_graph_0_0_2():
    """graph voor f(x) = 0 * x^2 + 0 * x + 2 is correct"""
    graph = check50.run("./graph").stdin("0").stdin("0").stdin("2").stdout()
    assert_graph(graph, "0_0_2.txt")

@check50.check(compiles)
def test_graph_0_0_25():
    """graph voor f(x) = 0 * x^2 + 0 * x + 2.5 is correct"""
    graph = check50.run("./graph").stdin("0").stdin("0").stdin("2.5").stdout()
    assert_graph(graph, "0_0_25.txt")

    
def assert_graph(graph: str, real_graph_file: str) -> None:
    graph_lines = [line for line in graph.split("\n") if line.strip()]

    if len(graph_lines) != 24:
        raise check50.Failure(f"expected exactly 24 lines of output, but found {len(graph_lines)}")

    check50.include(real_graph_file)
    with open(real_graph_file) as f:
        real_lines = [line.strip("\n") for line in f.readlines() if line.strip()]
        
    for i, (line, real_line) in enumerate(zip(graph_lines, real_lines)):
        if line != real_line:
            raise check50.Mismatch(
                real_line,
                line,
                help=f"This difference is on line: {i + 1}"
            )
    