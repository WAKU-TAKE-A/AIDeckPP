import math
import re
from dataclasses import dataclass

@dataclass
class TextChunk:
    text: str
    bold: bool = False
    italic: bool = False

def _tokenize_to_html(text: str, input_format: str) -> str:
    # Escape existing tags just in case
    text = text.replace('<b>', '&lt;b&gt;').replace('</b>', '&lt;/b&gt;')
    text = text.replace('<i>', '&lt;i&gt;').replace('</i>', '&lt;/i&gt;')
    
    if input_format == "asciidoc":
        # Asciidoc formatting
        # Bold & Italic (unconstrained)
        text = re.sub(r'\*\*__(.+?)__\*\*', r'<b><i>\1</i></b>', text)
        text = re.sub(r'__\*\*(.+?)\*\*__', r'<i><b>\1</b></i>', text)
        # Bold & Italic (constrained)
        text = re.sub(r'(^|[\s\W])\*_(.+?)_\*($|[\s\W])', r'\1<b><i>\2</i></b>\3', text)
        text = re.sub(r'(^|[\s\W])_\*(.+?)\*_($|[\s\W])', r'\1<i><b>\2</b></i>\3', text)
        
        # Unconstrained Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        # Constrained Bold
        text = re.sub(r'(^|[\s\W])\*(.+?)\*($|[\s\W])', r'\1<b>\2</b>\3', text)
        
        # Unconstrained Italic
        text = re.sub(r'__(.+?)__', r'<i>\1</i>', text)
        # Constrained Italic
        text = re.sub(r'(^|[\s\W])_(.+?)_($|[\s\W])', r'\1<i>\2</i>\3', text)
    else:
        # Markdown formatting
        # Bold: ** or __
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
        # Italic: * or _ (must not match inside words easily, but simple regex for markdown is usually fine unless specified)
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)
        
    return text

def parse_inline_formatting(text: str, input_format: str = "markdown") -> list[TextChunk]:
    if not text:
        return [TextChunk("")]

    html_text = _tokenize_to_html(text, input_format)
    
    chunks = []
    tokens = re.split(r'(<b>|</b>|<i>|</i>)', html_text)
    
    bold = False
    italic = False
    
    for token in tokens:
        if token == '<b>':
            bold = True
        elif token == '</b>':
            bold = False
        elif token == '<i>':
            italic = True
        elif token == '</i>':
            italic = False
        elif token:
            t = token.replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
            t = t.replace('&lt;i&gt;', '<i>').replace('&lt;/i&gt;', '</i>')
            chunks.append(TextChunk(text=t, bold=bold, italic=italic))
            
    if not chunks:
        chunks = [TextChunk("")]
        
    return chunks


def count_rendered_lines(text: str, chars_per_line: int = 0) -> int:
    """
    Count the number of rendered visual lines for a given text,
    taking into account hard returns (\n), soft returns (\x0b), 
    and line wrapping based on chars_per_line.
    
    If chars_per_line is 0 or less, wrapping is not calculated 
    (only explicit returns are counted).
    """
    if not text:
        return 1
        
    paragraphs = text.replace('\x0b', '\n').split('\n')
    total_lines = 0
    for p in paragraphs:
        if not p:
            total_lines += 1
            continue
            
        if chars_per_line <= 0:
            total_lines += 1
        else:
            total_lines += math.ceil(len(p) / chars_per_line)
            
    return total_lines
