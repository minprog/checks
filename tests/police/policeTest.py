from checkpy import *

# === STAP 1: Node en Edge ==========================================
@test()
def test_node_and_edge_basic():
    """Basis tests voor Node en Edge classes"""
    police = getModule()

    a = police.Node("Alice")
    b = police.Node("Bob")

    assert repr(a) == "Alice", f"De representatie van Node moet 'Alice' zijn, niet {repr(a)}"
    assert isinstance(a.edges, list), "Node.edges moet een lijst zijn"
    assert len(a.edges) == 0, "Nieuwe Node moet beginnen zonder edges"

    e = police.Edge(a, b)
    assert repr(e) in ("Alice - Bob", "Bob - Alice"), f"Edge representatie klopt niet: {repr(e)}"
    assert e.node1 in (a, b), "node1 is niet correct"
    assert e.node2 in (a, b), "node2 is niet correct"
    assert e.other(a) == b, "Edge.other(node) geeft niet de andere node terug"
    assert e.other(b) == a, "Edge.other(node) geeft niet de andere node terug"

    a.add_edge(e)
    assert e in a.edges, "Edge wordt niet toegevoegd aan Node.edges"


@test()
def test_edge_other_valueerror():
    """Edge.other() geeft een ValueError voor onbekende node"""
    police = getModule()

    a = police.Node("Alice")
    b = police.Node("Bob")
    c = police.Node("Charlie")
    e = police.Edge(a, b)
    try:
        e.other(c)
    except ValueError:
        return True
    else:
        raise AssertionError("Edge.other() zou een ValueError moeten geven als node niet in edge zit.")


# === STAP 2: Graph basis ===========================================
@test()
def test_graph_add_person_and_contact():
    """Basis tests voor Graph class, add_person en add_contact"""
    police = getModule()

    g = police.Graph()
    g.add_person("Alice")
    g.add_person("Bob")
    g.add_contact("Alice", "Bob")

    assert len(g.all_people) == 2, f"Er moeten 2 personen zijn, maar er zijn {len(g.all_people)}"
    assert len(g.all_contacts) == 1, f"Er moet 1 contact zijn, maar er zijn {len(g.all_contacts)}"

    rep = repr(g)
    assert "Alice" in rep and "Bob" in rep, f"__repr__() van Graph is niet correct: {rep}"


# === STAP 3: load_from_file ========================================
@test()
def test_load_from_file():
    """Graph.load_from_file() werkt correct"""
    only("police.py")
    
    with open("small_contacts.csv", "w") as f:
        f.write("Person1,Person2,Method\nAlice,Bob,phone\nBob,Charlie,meeting\nCharlie,Alice,meeting\n")

    police = getModule()
    g = police.Graph._function.load_from_file("small_contacts.csv") # TODO checkpy should not wrap this in checkpy.entities.function.Function

    people = sorted([n.name for n in g.all_people])
    assert people == ["Alice", "Bob", "Charlie"], f"Verkeerde personen geladen: {people}"

    edges = g.all_contacts

    expected = [("Alice", "Bob"), ("Alice", "Charlie"), ("Bob", "Charlie")]

    assert len(edges) == len(expected), f"Verkeerd aantal edges geladen: {edges}"

    for name1, name2 in expected:
        found = False
        
        for edge in edges:
            if (edge.node1.name == name1 and edge.node2.name == name2 or
               edge.node1.name == name2 and edge.node2.name == name1):
                found = True
                break
        
        if not found:
            raise AssertionError(f"Contact tussen {name1} en {name2} niet gevonden in geladen edges: {edges}")
            

# === STAP 4: get_most_contacts en get_direct_contacts ==============
@test()
def test_get_most_contacts():
    """Graph.get_most_contacts() werkt correct"""
    police = getModule()

    g = police.Graph()
    g.add_person("Alice")
    g.add_person("Bob")
    g.add_person("Charlie")

    g.add_contact("Alice", "Bob")
    g.add_contact("Bob", "Charlie")
    g.add_contact("Alice", "Charlie")

    most = g.get_most_contacts()
    assert most.name in ("Alice", "Bob", "Charlie"), f"Verkeerde persoon met meeste contacten: {most}"


@test()
def test_get_direct_contacts():
    """Graph.get_direct_contacts() werkt correct"""
    police = getModule()

    g = police.Graph()
    g.add_person("Alice")
    g.add_person("Bob")
    g.add_person("Charlie")

    g.add_contact("Alice", "Bob")
    g.add_contact("Bob", "Charlie")

    contacts = [n.name for n in g.get_direct_contacts("Bob")]
    
    assert set(contacts) == {"Alice", "Charlie"}, f"Directe contacten van Bob zijn verkeerd: {contacts}"

    try:
        g.get_direct_contacts("Diana")
    except ValueError:
        return True
    else:
        raise AssertionError("get_direct_contacts() zou een ValueError moeten geven voor onbekende naam.")


# === STAP 5: get_indirect_contacts =================================
@test()
def test_indirect_contacts():
    """Graph.get_indirect_contacts() werkt correct"""
    police = getModule()

    g = police.Graph()

    g.add_person("Alice")
    g.add_person("Bob")
    g.add_person("Charlie")
    g.add_person("Diana")

    g.add_contact("Alice", "Bob")
    g.add_contact("Bob", "Charlie")
    g.add_contact("Charlie", "Diana")

    indirect = [n.name for n in g.get_indirect_contacts("Alice")]
    assert "Charlie" in indirect and "Diana" in indirect, f"Indirecte contacten van Alice zijn onvolledig: {indirect}"
    assert "Bob" not in indirect, "Direct contact mag niet in indirecte contacten staan"


# === STAP 6: get_groups ============================================
@test()
def test_get_groups():
    """Graph.get_groups() werkt correct"""
    police = getModule()

    g = police.Graph()
    g.add_person("Alice")
    g.add_person("Bob")
    g.add_person("Charlie")
    g.add_person("Diana")
    g.add_person("Eve")

    g.add_contact("Alice", "Bob")
    g.add_contact("Charlie", "Diana")
    g.add_contact("Diana", "Eve")

    groups = g.get_groups()
    group_sets = [set(n.name for n in s) for s in groups]
    expected = [{"Alice", "Bob"}, {"Charlie", "Diana", "Eve"}]
    assert any(s == expected[0] for s in group_sets), f"Groep 1 ({expected[0]}) niet gevonden"
    assert any(s == expected[1] for s in group_sets), f"Groep 2 ({expected[1]}) niet gevonden"


# === STAP 7: get_triangles ========================================
@test()
def test_get_triangles():
    """Graph.get_triangles() werkt correct"""
    police = getModule()

    g = police.Graph()

    g.add_person("Alice")
    g.add_person("Bob")
    g.add_person("Charlie")
    g.add_person("Diana")

    g.add_contact("Alice", "Bob")
    g.add_contact("Bob", "Charlie")
    g.add_contact("Charlie", "Alice")
    g.add_contact("Charlie", "Diana")

    triangles = g.get_triangles("Charlie")
    tri_sets = [set(n.name for n in t) for t in triangles]
    assert {"Alice", "Bob", "Charlie"} in tri_sets, f"Driehoek {tri_sets} mist {'Alice', 'Bob', 'Charlie'}"

@passed(test_indirect_contacts, test_get_groups, test_get_triangles)
def test_actual_files():
    """Test met echte bestand (contacts.csv)"""
    only("police.py")
    includeFromTests("contacts.csv")
    
    police = getModule()

    g = police.Graph._function.load_from_file("contacts.csv")
    if g.get_most_contacts().name != "Luca":
        raise AssertionError("Persoon met meeste contacten is onjuist")
    
    direct = [n.name for n in g.get_direct_contacts("Luca")]
    if set(direct) != {"Erik", "Youssef", "Alejandro", "Jelle", "Jesse", "Nikolai", "Thomas", "Peter", "Omar", "Marco", "Rick", "Simon", "Kenji", "Lennart"}:
        raise AssertionError("Directe contacten van Luca (persoon met meeste contacten) zijn onjuist")
    
    Node = police.Node
    assert "Akira" in [n.name for n in g.get_indirect_contacts("Luca")], "Indirecte contacten van Luca zijn onjuist"
    assert "Ivan" in [n.name for n in g.get_indirect_contacts("Roel")], "Indirecte contacten van Roel zijn onjuist"
    assert "Peter" not in [n.name for n in g.get_indirect_contacts("Marco")], "Indirecte contacten van Marco zijn onjuist"
    assert "Erik" not in [n.name for n in g.get_indirect_contacts("Hugo")], "Indirecte contacten van Hugo zijn onjuist"

    groups = g.get_groups()
    group_sizes = sorted([len(s) for s in groups])
    if group_sizes != [2, 2, 3, 50]:
        raise AssertionError(f"Grootte van groepen is onjuist: {group_sizes}")
    
    triangles = g.get_triangles("Luca")
    tri_sets = [set(n.name for n in t) for t in triangles]
    
    expected_triangles = [
        {'Luca', 'Jesse', 'Erik'},
        {'Peter', 'Luca', 'Erik'},
        {'Erik', 'Luca', 'Marco'},
        {'Simon', 'Luca', 'Erik'},
        {'Lennart', 'Luca', 'Erik'},
        {'Alejandro', 'Luca', 'Thomas'},
        {'Alejandro', 'Rick', 'Luca'},
        {'Luca', 'Jesse', 'Jelle'},
        {'Thomas', 'Luca', 'Jesse'},
        {'Peter', 'Luca', 'Jesse'},
        {'Rick', 'Nikolai', 'Luca'},
        {'Peter', 'Luca', 'Marco'},
        {'Lennart', 'Peter', 'Luca'},
        {'Lennart', 'Luca', 'Marco'}
    ]

    for expected in expected_triangles:
        if expected not in tri_sets:
            raise AssertionError(f"Driehoek met {expected} ontbreekt")
