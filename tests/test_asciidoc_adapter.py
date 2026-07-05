import pytest
from pathlib import Path
from deck2pptx.asciidoc_adapter import load_asciidoc
from deck2pptx.models import Text, BulletList, Image, Table, Flow, Comparison, Timeline, Tree, Split, CodeBlock

def test_asciidoc_metadata(tmp_path):
    content = """= My Presentation Title
:theme: custom_theme
:toc:
:toc_title: Custom Agenda
:footer: My Company Footer
:date: 2026-07-01
:indent: 4

== Slide 1
Some body text
"""
    f = tmp_path / "test.adoc"
    f.write_text(content, encoding='utf-8')
    deck = load_asciidoc(f)
    
    assert deck.title == "My Presentation Title"
    assert deck.theme == "custom_theme"
    assert deck.toc is True
    assert deck.toc_title == "Custom Agenda"
    assert deck.footer == "My Company Footer"
    assert deck.date == "2026-07-01"
    assert deck.indent == 4

def test_asciidoc_slides_split(tmp_path):
    content = """= Presentation Title

== Slide A
Body A

=== Slide B
Body B

==== Slide C
This should be body, not a new slide.
"""
    f = tmp_path / "test.adoc"
    f.write_text(content, encoding='utf-8')
    deck = load_asciidoc(f)
    
    assert len(deck.slides) == 3
    assert deck.slides[0].title == "Presentation Title"
    assert deck.slides[1].title == "Slide A"
    assert deck.slides[2].title == "Slide B"
    
    # Check that Slide C is body text inside Slide B
    elements = deck.slides[2].elements
    assert any("Slide C" in getattr(el, 'content', '') for el in elements)

def test_asciidoc_basic_elements(tmp_path):
    content = """== Slide 1
This is normal text.

* Item 1
** Item 1.1
- Item 2
-- Item 2.1

image::img/sample.png[Sample Caption]
"""
    f = tmp_path / "test.adoc"
    f.write_text(content, encoding='utf-8')
    deck = load_asciidoc(f)
    
    elements = deck.slides[0].elements
    assert len(elements) == 3
    
    assert isinstance(elements[0], Text)
    assert elements[0].content == "This is normal text."
    
    bl = elements[1]
    assert isinstance(bl, BulletList)
    assert len(bl.items) == 4
    assert bl.items[0].text == "Item 1"
    assert bl.items[0].level == 0
    assert bl.items[1].text == "Item 1.1"
    assert bl.items[1].level == 1
    assert bl.items[2].text == "Item 2"
    assert bl.items[2].level == 0
    assert bl.items[3].text == "Item 2.1"
    assert bl.items[3].level == 1
    
    img = elements[2]
    assert isinstance(img, Image)
    assert img.source == "img/sample.png"
    assert img.caption == "Sample Caption"

def test_asciidoc_tables(tmp_path):
    # Case 1: Standard PSV (No attributes) -> 1st row is always header
    content1 = """== Slide 1
|===
|Col 1 |Col 2

|Cell 1-1
|Cell 1-2

|Cell 2-1
|Cell 2-2
|===
"""
    f1 = tmp_path / "table1.adoc"
    f1.write_text(content1, encoding='utf-8')
    deck1 = load_asciidoc(f1)
    t1 = deck1.slides[0].elements[0]
    assert isinstance(t1, Table)
    assert t1.headers == ["Col 1", "Col 2"]
    assert t1.rows == [["Cell 1-1", "Cell 1-2"], ["Cell 2-1", "Cell 2-2"]]

    # Case 2: CSV Table with options="header"
    content2 = """== Slide 2
[format="csv", options="header"]
|===
Col A,Col B
Val A1,Val B1
Val A2,Val B2
|===
"""
    f2 = tmp_path / "table2.adoc"
    f2.write_text(content2, encoding='utf-8')
    deck2 = load_asciidoc(f2)
    t2 = deck2.slides[0].elements[0]
    assert isinstance(t2, Table)
    assert t2.headers == ["Col A", "Col B"]
    assert t2.rows == [["Val A1", "Val B1"], ["Val A2", "Val B2"]]

    # Case 3: CSV Table without options="header" -> No headers
    content3 = """== Slide 3
[format="csv"]
|===
Val A1,Val B1
Val A2,Val B2
|===
"""
    f3 = tmp_path / "table3.adoc"
    f3.write_text(content3, encoding='utf-8')
    deck3 = load_asciidoc(f3)
    t3 = deck3.slides[0].elements[0]
    assert isinstance(t3, Table)
    assert t3.headers == []
    assert t3.rows == [["Val A1", "Val B1"], ["Val A2", "Val B2"]]

def test_asciidoc_business_blocks(tmp_path):
    content = """== Slide 1

[flow]
----
A -> B
----

[comparison]
----
Left:
- a
Right:
- b
----

[timeline]
----
2026: Phase 1 - Desc
----

[tree]
----
Root
  Child
----

[source, python]
----
print("hello")
----
"""
    f = tmp_path / "test.adoc"
    f.write_text(content, encoding='utf-8')
    deck = load_asciidoc(f)
    
    elements = deck.slides[0].elements
    assert len(elements) == 5
    
    assert isinstance(elements[0], Flow)
    assert elements[0].edges[0].from_node == "A"
    assert elements[0].edges[0].to_node == "B"
    
    assert isinstance(elements[1], Comparison)
    assert elements[1].columns[0].label == "Left"
    assert elements[1].columns[0].items == ["a"]
    
    assert isinstance(elements[2], Timeline)
    assert elements[2].events[0].label == "2026"
    assert elements[2].events[0].title == "Phase 1"
    assert elements[2].events[0].description == "Desc"
    
    assert isinstance(elements[3], Tree)
    assert tree_node_label(elements[3].root) == "Root"
    assert tree_node_label(elements[3].root.children[0]) == "Child"
    
    assert isinstance(elements[4], CodeBlock)
    assert elements[4].code == "print(\"hello\")"
    assert elements[4].language == "python"

def tree_node_label(node):
    return node.label

def test_asciidoc_split_panel(tmp_path):
    content = """== Slide 1
// split h
// panel "Left Panel"
Left content.
// panel "Right Panel"
Right content.
// /split
"""
    f = tmp_path / "test.adoc"
    f.write_text(content, encoding='utf-8')
    deck = load_asciidoc(f)
    
    elements = deck.slides[0].elements
    assert len(elements) == 1
    
    split = elements[0]
    assert isinstance(split, Split)
    assert split.direction == "horizontal"
    assert len(split.panels) == 2
    assert split.panels[0].title == "Left Panel"
    assert isinstance(split.panels[0].elements[0], Text)
    assert split.panels[0].elements[0].content == "Left content."
