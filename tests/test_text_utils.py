import pytest
from deck2pptx.text_utils import parse_inline_formatting, count_rendered_lines, TextChunk

def test_parse_inline_formatting_markdown():
    # Basic
    chunks = parse_inline_formatting("Hello **world**!", input_format="markdown")
    assert chunks[0] == TextChunk("Hello ", False, False)
    assert chunks[1] == TextChunk("world", True, False)
    assert chunks[2] == TextChunk("!", False, False)

    # Italic
    chunks = parse_inline_formatting("This is *italic* text", input_format="markdown")
    assert chunks[1] == TextChunk("italic", False, True)

    # Multiple
    chunks = parse_inline_formatting("**Bold** and *Italic*", input_format="markdown")
    assert chunks[0] == TextChunk("Bold", True, False)
    assert chunks[1] == TextChunk(" and ", False, False)
    assert chunks[2] == TextChunk("Italic", False, True)

    # Empty
    assert parse_inline_formatting("", "markdown") == [TextChunk("")]

def test_parse_inline_formatting_asciidoc():
    # Unconstrained Bold
    chunks = parse_inline_formatting("Unconstrained **bold** text", input_format="asciidoc")
    assert chunks[1] == TextChunk("bold", True, False)

    # Constrained Bold
    chunks = parse_inline_formatting("Constrained *bold* text", input_format="asciidoc")
    assert chunks[1] == TextChunk("bold", True, False)

    # Unconstrained Italic
    chunks = parse_inline_formatting("Unconstrained __italic__ text", input_format="asciidoc")
    assert chunks[1] == TextChunk("italic", False, True)

    # Constrained Italic
    chunks = parse_inline_formatting("Constrained _italic_ text", input_format="asciidoc")
    assert chunks[1] == TextChunk("italic", False, True)

    # Bold and Italic Unconstrained
    chunks = parse_inline_formatting("**__bold italic__**", input_format="asciidoc")
    assert chunks[0] == TextChunk("bold italic", True, True)

    # Bold and Italic Constrained
    chunks = parse_inline_formatting(" *_bold italic_* ", input_format="asciidoc")
    assert chunks[1] == TextChunk("bold italic", True, True)

def test_count_rendered_lines():
    # Basic explicit newlines
    assert count_rendered_lines("Line 1\nLine 2") == 2
    assert count_rendered_lines("Line 1\nLine 2\nLine 3") == 3

    # Soft returns
    assert count_rendered_lines("Line 1\x0bLine 2") == 2

    # Wrapping
    assert count_rendered_lines("12345", chars_per_line=2) == 3 # ceil(5/2) = 3
    assert count_rendered_lines("123\n12", chars_per_line=2) == 3 # ceil(3/2) + ceil(2/2) = 2 + 1 = 3

    # Empty or zero cases
    assert count_rendered_lines("") == 1
    assert count_rendered_lines("Line", chars_per_line=0) == 1
