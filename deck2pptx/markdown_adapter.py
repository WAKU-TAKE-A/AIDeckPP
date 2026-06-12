import re
import yaml
from pathlib import Path
from .models import Deck, Slide, Text, BulletList, Image, Table, Gallery, Flow, FlowNode, FlowEdge

def load_markdown(file_path: str | Path) -> Deck:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    deck = Deck()
    
    # 1. Parse Front Matter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1]) or {}
                deck.title = fm.get('title')
                deck.orientation = fm.get('orientation', 'landscape')
                deck.theme = fm.get('theme', 'default')
            except:
                pass
            content = parts[2].lstrip()
            
    # 2. Split into slides
    lines = content.splitlines()
    slides_data = []
    current_slide_lines = []
    
    for line in lines:
        if line.startswith('# ') or line.startswith('## '):
            if current_slide_lines:
                slides_data.append(current_slide_lines)
            current_slide_lines = [line]
        else:
            current_slide_lines.append(line)
            
    if current_slide_lines:
        slides_data.append(current_slide_lines)
        
    for slide_lines in slides_data:
        if not slide_lines:
            continue
            
        header_line = slide_lines[0]
        title = header_line.lstrip('#').strip()
        
        slide = Slide(title=title)
        
        # If the slide has ONLY a title, maybe it's a title layout
        # We can look for metadata in the slide (optional, keeping it simple)
        
        i = 1
        current_text = []
        current_bullets = []
        current_table = []
        
        def commit_text():
            if current_text:
                slide.elements.append(Text(content=' '.join(current_text)))
                current_text.clear()
        
        def commit_bullets():
            if current_bullets:
                slide.elements.append(BulletList(items=list(current_bullets)))
                current_bullets.clear()
                
        def commit_table():
            if current_table:
                # First row is header, second is divider, rest are rows
                headers = []
                rows = []
                if len(current_table) > 2 and '---' in current_table[1]:
                    headers = [c.strip() for c in current_table[0].strip('|').split('|')]
                    for r in current_table[2:]:
                        rows.append([c.strip() for c in r.strip('|').split('|')])
                else:
                    for r in current_table:
                        rows.append([c.strip() for c in r.strip('|').split('|')])
                slide.elements.append(Table(headers=headers if headers else None, rows=rows))
                current_table.clear()
                
        while i < len(slide_lines):
            line = slide_lines[i].strip()
            if not line:
                commit_text()
                commit_bullets()
                commit_table()
                i += 1
                continue
                
            # Table
            if line.startswith('|') and line.endswith('|'):
                commit_text()
                commit_bullets()
                current_table.append(line)
                i += 1
                continue
            else:
                commit_table()
                
            # Bullets
            if line.startswith('- ') or line.startswith('* '):
                commit_text()
                current_bullets.append(line[2:].strip())
                i += 1
                continue
            else:
                commit_bullets()
                
            # Flow Block
            if line.startswith('```flow'):
                commit_text()
                direction = 'horizontal'
                if 'vertical' in line:
                    direction = 'vertical'
                
                i += 1
                nodes = []
                edges = []
                while i < len(slide_lines) and not slide_lines[i].strip().startswith('```'):
                    fl = slide_lines[i].strip()
                    if '->' in fl:
                        fr, to = fl.split('->')
                        edges.append(FlowEdge(from_node=fr.strip(), to_node=to.strip()))
                    elif ':' in fl:
                        nid, nlabel = fl.split(':', 1)
                        nodes.append(FlowNode(id=nid.strip(), label=nlabel.strip()))
                    i += 1
                
                if nodes:
                    slide.elements.append(Flow(direction=direction, nodes=nodes, edges=edges))
                i += 1
                continue
                
            # Image
            img_match = re.match(r'^!\[.*?\]\((.*?)\)$', line)
            if img_match:
                commit_text()
                img_src = img_match.group(1)
                
                # Check if last element is Gallery, and append. If Image, convert to Gallery.
                if slide.elements and isinstance(slide.elements[-1], Gallery):
                    slide.elements[-1].images.append(Image(source=img_src))
                elif slide.elements and isinstance(slide.elements[-1], Image):
                    prev_img = slide.elements.pop()
                    slide.elements.append(Gallery(images=[prev_img, Image(source=img_src)]))
                else:
                    slide.elements.append(Image(source=img_src))
                i += 1
                continue
                
            # Plain Text
            current_text.append(line)
            i += 1
            
        commit_text()
        commit_bullets()
        commit_table()
        
        deck.slides.append(slide)

    # Set layout hints based on headers
    if deck.slides and deck.slides[0].title and not deck.slides[0].elements:
        deck.slides[0].layout_hint = 'title'

    return deck
