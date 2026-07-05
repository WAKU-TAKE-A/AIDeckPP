import re
import csv
from pathlib import Path
from .models import (
    Deck, Slide, Text, BulletList, ListItem, Image, Table, Gallery,
    Flow, FlowNode, FlowEdge, Split, Panel, Mermaid, Comparison,
    ComparisonColumn, Timeline, TimelineEvent, CodeBlock, Tree, TreeNode
)

def load_asciidoc(file_path: str | Path) -> Deck:
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    deck = Deck()
    
    lines = content.splitlines()
    
    # 1. Parse Metadata / Document Attributes
    title_parsed = False
    title_line = None
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            if title_parsed or deck.theme != 'default' or deck.footer or deck.date:
                i += 1
                break
            i += 1
            continue
            
        if line.startswith('==') or line.startswith('==='):
            break
            
        if line.startswith('=') and not line.startswith('=='):
            deck.title = line.lstrip('=').strip()
            title_parsed = True
            title_line = lines[i]
            i += 1
            continue
            
        m = re.match(r'^:([^:]+):(.*)$', line)
        if m:
            key = m.group(1).strip().lower()
            val = m.group(2).strip()
            
            if key == 'theme':
                deck.theme = val
            elif key == 'toc':
                deck.toc = val.lower() not in ('false', 'no') if val else True
            elif key == 'toc_title':
                deck.toc_title = val
            elif key == 'indent':
                try:
                    deck.indent = int(val)
                except:
                    pass
            elif key == 'content_align':
                deck.content_align = val
            elif key == 'footer':
                deck.footer = val
            elif key == 'date':
                deck.date = val
            i += 1
            continue
            
        break

    body_lines = lines[i:]
    if title_line:
        body_lines.insert(0, title_line)
    
    # 2. Parse slide controls (comments)
    def parse_asciidoc_comment(line):
        import shlex
        m = re.match(r'^//\s*(.*)$', line.strip())
        if not m: return []
        content = m.group(1).strip()
        
        commands = []
        current = []
        in_quotes = False
        for char in content:
            if char == '"':
                in_quotes = not in_quotes
                current.append(char)
            elif char == ';' and not in_quotes:
                commands.append(''.join(current).strip())
                current = []
            else:
                current.append(char)
        if current:
            commands.append(''.join(current).strip())
            
        parsed_cmds = []
        for cmd in commands:
            if not cmd: continue
            try:
                tokens = shlex.split(cmd)
                if not tokens: continue
                
                if '=' in tokens[0] and tokens[0] != '=':
                    parts = tokens[0].split('=', 1)
                    cmd_name = parts[0].lower()
                    args = [parts[1]] + tokens[1:]
                else:
                    cmd_name = tokens[0].lower()
                    args = tokens[1:]
                    
                if cmd_name in ('l', 'layout'): cmd_name = 'layout'
                elif cmd_name in ('sub', 'subtitle'): cmd_name = 'subtitle'
                elif cmd_name in ('ph', 'place', 'placeholder'): cmd_name = 'placeholder'
                elif cmd_name in ('new', 'new_page', 'newpage'): cmd_name = 'newpage'
                elif cmd_name in ('align', 'content_align', 'valign'): cmd_name = 'content_align'
                elif cmd_name in ('gal', 'gallery'): cmd_name = 'gallery'
                
                parsed_args = []
                for arg in args:
                    if '=' in arg:
                        k, v = arg.split('=', 1)
                        parsed_args.append((k, v))
                    else:
                        parsed_args.append(arg)
                parsed_cmds.append((cmd_name, parsed_args))
            except:
                pass
        return parsed_cmds

    # 3. Split into slides
    slides_data = []
    current_slide_lines = []
    pending_layout = None

    def append_current_slide():
        if current_slide_lines and not all(not l.strip() for l in current_slide_lines):
            slides_data.append((pending_layout, list(current_slide_lines)))

    def has_heading(lines):
        return any(re.match(r'^={1,3}\s+', l) for l in lines)

    def layout_arg(args):
        if not args:
            return None
        if type(args[0]) == tuple:
            return args[0][1]
        return args[0]

    for line in body_lines:
        sline = line.strip()
        cmds = parse_asciidoc_comment(sline)
        has_newpage = any(cmd == 'newpage' for cmd, _ in cmds)
        has_layout = any(cmd == 'layout' for cmd, _ in cmds)
        
        if has_newpage:
            append_current_slide()
            new_layout = None
            for cmd, args in cmds:
                if cmd in ('newpage', 'layout') and args:
                    new_layout = layout_arg(args)
            pending_layout = new_layout
            current_slide_lines = [""]
            other_cmds = [(c, a) for c, a in cmds if c not in ('newpage', 'layout')]
            if other_cmds:
                current_slide_lines.append(line)
            continue
            
        if has_layout and not has_newpage and len(cmds) == 1:
            for cmd, args in cmds:
                if cmd == 'layout' and args:
                    if has_heading(current_slide_lines) and current_slide_lines[-1].strip():
                        current_slide_lines.append(line)
                    else:
                        append_current_slide()
                        pending_layout = layout_arg(args)
                        current_slide_lines = []
            continue
            
        if re.match(r'^={1,3}\s+', line):
            if current_slide_lines:
                has_content = False
                for l in current_slide_lines:
                    if l.strip() and not re.match(r'^//', l.strip()):
                        has_content = True
                        break
                if not has_content:
                    current_slide_lines.append(line)
                else:
                    slides_data.append((pending_layout, current_slide_lines))
                    current_slide_lines = [line]
                    pending_layout = None
            else:
                current_slide_lines = [line]
        else:
            current_slide_lines.append(line)
            
    if current_slide_lines:
        slides_data.append((pending_layout, current_slide_lines))
        
    section_counter = 0
        
    for layout_hint, slide_lines in slides_data:
        if not slide_lines:
            continue
            
        title_line_idx = -1
        for idx, ln in enumerate(slide_lines):
            if re.match(r'^={1,3}\s+', ln):
                title_line_idx = idx
                if re.match(r'^==\s+', ln):
                    section_counter += 1
                break
        
        if title_line_idx >= 0:
            match = re.match(r'^(=+)\s+', slide_lines[title_line_idx])
            level = len(match.group(1)) if match else 1
            title = slide_lines[title_line_idx].lstrip('=').strip()
        else:
            title = ""
            level = 1
            
        i = 0
            
        slide = Slide(title=title, layout_hint=layout_hint, section_no=str(section_counter), level=level)
        
        current_text = []
        current_bullets = []
        current_placeholder = None
        
        active_split = None
        active_panel = None
        active_gallery = None
        
        pending_table_attr = None
        pending_block_type = None
        pending_code_lang = None
        
        def get_target_list():
            if active_panel:
                return active_panel.elements
            return slide.elements
        
        def commit_text():
            nonlocal active_gallery
            if current_text:
                get_target_list().append(Text(content=join_text_lines(current_text), placeholder=current_placeholder))
                current_text.clear()
                active_gallery = None

        def join_text_lines(lines):
            content = ""
            for text in lines:
                if not content:
                    content = text
                elif content.endswith('\n') or text.startswith('\n'):
                    content += text
                else:
                    content += ' ' + text
            return content

        def normalize_text_line(raw_text):
            text = raw_text.strip()
            hard_break = len(raw_text) - len(raw_text.rstrip(' ')) >= 2
            text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
            text = text.replace('\\n', '\n')
            if hard_break and not text.endswith('\n'):
                text += '\n'
            return text
        
        def commit_bullets():
            nonlocal active_gallery
            if current_bullets:
                get_target_list().append(BulletList(items=list(current_bullets), placeholder=current_placeholder))
                current_bullets.clear()
                active_gallery = None

        while i < len(slide_lines):
            if i == title_line_idx:
                i += 1
                continue

            raw_line = slide_lines[i]
            line = raw_line.strip()
            
            cmds = parse_asciidoc_comment(line)
            if cmds:
                handled_line = False
                for cmd, args in cmds:
                    if cmd == 'subtitle':
                        slide.subtitle = args[0] if args else None
                        handled_line = True
                    elif cmd == 'layout':
                        slide.layout_hint = args[0] if args else None
                        handled_line = True
                    elif cmd == 'content_align':
                        slide.content_align = args[0] if args else None
                        handled_line = True
                    elif cmd == 'placeholder':
                        current_placeholder = args[0] if args else None
                        if len(args) > 1:
                            hidden_val = normalize_text_line(args[1])
                            commit_text()
                            commit_bullets()
                            get_target_list().append(Text(content=hidden_val, placeholder=current_placeholder))
                            current_placeholder = None
                        handled_line = True
                    elif cmd in ('v', 'value'):
                        if current_placeholder and args:
                            hidden_val = normalize_text_line(args[0])
                            commit_text()
                            commit_bullets()
                            get_target_list().append(Text(content=hidden_val, placeholder=current_placeholder))
                            current_placeholder = None
                        handled_line = True
                    elif cmd == 'gallery':
                        commit_text()
                        commit_bullets()
                        cols = None
                        if args:
                            try:
                                cols = int(args[0])
                            except:
                                pass
                        active_gallery = Gallery(images=[], columns=cols, placeholder=current_placeholder)
                        get_target_list().append(active_gallery)
                        handled_line = True
                    elif cmd == 'split':
                        commit_text()
                        commit_bullets()
                        direction = 'horizontal'
                        if args:
                            arg = args[0]
                            if isinstance(arg, tuple) and arg[0] == 'direction':
                                direction = 'horizontal' if arg[1] in ('h', 'horizontal') else 'vertical'
                            elif isinstance(arg, str):
                                direction = 'horizontal' if arg in ('h', 'horizontal') else 'vertical'
                        active_split = Split(direction=direction, panels=[], placeholder=current_placeholder)
                        slide.elements.append(active_split)
                        active_panel = Panel()
                        active_split.panels.append(active_panel)
                        handled_line = True
                    elif cmd == 'panel':
                        commit_text()
                        commit_bullets()
                        title_val = None
                        if args:
                            arg = args[0]
                            if isinstance(arg, tuple) and arg[0] == 'title':
                                title_val = arg[1]
                            elif isinstance(arg, str):
                                title_val = arg
                        if active_split:
                            if len(active_split.panels) == 1 and not active_split.panels[0].elements and active_split.panels[0].title is None:
                                active_split.panels.clear()
                            active_panel = Panel(title=title_val)
                            active_split.panels.append(active_panel)
                        handled_line = True
                    elif cmd == '/split':
                        commit_text()
                        commit_bullets()
                        active_split = None
                        active_panel = None
                        handled_line = True
                if handled_line:
                    i += 1
                    continue
            
            if not line:
                commit_text()
                commit_bullets()
                active_gallery = None
                i += 1
                continue
                
            if re.match(r'^\.([^ \t].*)$', line):
                i += 1
                continue
                
            if line.startswith('[') and line.endswith(']'):
                attr_content = line[1:-1].strip()
                if 'format=' in attr_content or 'options=' in attr_content or '%header' in attr_content:
                    pending_table_attr = attr_content
                else:
                    parts = [p.strip() for p in attr_content.split(',')]
                    block_name = parts[0].lower()
                    if block_name == 'source':
                        pending_block_type = 'code'
                        if len(parts) > 1:
                            pending_code_lang = parts[1]
                    else:
                        pending_block_type = block_name
                i += 1
                continue

            if line.startswith('----'):
                commit_text()
                commit_bullets()
                active_gallery = None
                
                block_lines = []
                i += 1
                while i < len(slide_lines) and not slide_lines[i].strip().startswith('----'):
                    block_lines.append(slide_lines[i])
                    i += 1
                i += 1
                
                if pending_block_type == 'flow':
                    direction = 'horizontal'
                    nodes = []
                    edges = []
                    for fl in block_lines:
                        fl_strip = fl.strip()
                        if not fl_strip: continue
                        edge_match = re.search(r'(.+?)\s*-+>\s*(.+)', fl_strip)
                        if edge_match:
                            edges.append(FlowEdge(from_node=edge_match.group(1).strip(), to_node=edge_match.group(2).strip()))
                        else:
                            node_match = re.match(r'^([^\[\(\{]+?)\s*[\[\(\{](.+?)[\]\)\}]\s*$', fl_strip)
                            if node_match:
                                nid = node_match.group(1).strip()
                                nlabel = node_match.group(2).strip()
                                if nlabel.startswith('"') and nlabel.endswith('"'):
                                    nlabel = nlabel[1:-1]
                                nodes.append(FlowNode(id=nid, label=nlabel))
                                
                    get_target_list().append(Flow(direction=direction, nodes=nodes, edges=edges, placeholder=current_placeholder))
                    
                elif pending_block_type == 'comparison':
                    columns = []
                    current_col_label = None
                    current_col_items = []
                    for cl in block_lines:
                        cl_strip = cl.strip()
                        if not cl_strip: continue
                        if cl_strip.endswith(':'):
                            if current_col_label is not None:
                                columns.append(ComparisonColumn(label=current_col_label, items=current_col_items))
                            current_col_label = cl_strip[:-1].strip()
                            current_col_items = []
                        elif cl_strip.startswith('- ') or cl_strip.startswith('* '):
                            current_col_items.append(cl_strip[2:].strip())
                            
                    if current_col_label is not None:
                        columns.append(ComparisonColumn(label=current_col_label, items=current_col_items))
                    
                    get_target_list().append(Comparison(title=None, columns=columns, placeholder=current_placeholder))
                    
                elif pending_block_type == 'timeline':
                    events = []
                    for tl in block_lines:
                        tl_strip = tl.strip()
                        if not tl_strip: continue
                        if ':' in tl_strip:
                            label, rest = tl_strip.split(':', 1)
                            title = rest.strip()
                            desc = None
                            if ' - ' in title:
                                title, desc = title.split(' - ', 1)
                            events.append(TimelineEvent(label=label.strip(), title=title.strip(), description=desc.strip() if desc else None))
                    get_target_list().append(Timeline(events=events, placeholder=current_placeholder))
                    
                elif pending_block_type == 'mermaid':
                    get_target_list().append(Mermaid(code='\n'.join(block_lines), placeholder=current_placeholder))
                    
                elif pending_block_type == 'tree':
                    tree_lines = [l for l in block_lines if l.strip()]
                    positive_indents = [
                        len(tl) - len(tl.lstrip())
                        for tl in tree_lines
                        if len(tl) - len(tl.lstrip()) > 0
                    ]
                    tree_indent_size = min(positive_indents) if positive_indents else (deck.indent if deck.indent else 2)

                    nodes_by_level = {}
                    root = None
                    for raw_tree_line in tree_lines:
                        indent_spaces = len(raw_tree_line) - len(raw_tree_line.lstrip())
                        level = indent_spaces // tree_indent_size
                        node = TreeNode(label=raw_tree_line.strip())
                        nodes_by_level[level] = node
                        if level == 0 and not root:
                            root = node
                        elif level > 0 and (level - 1) in nodes_by_level:
                            nodes_by_level[level - 1].children.append(node)
                    if root:
                        get_target_list().append(Tree(root=root, placeholder=current_placeholder))
                        
                else:
                    get_target_list().append(CodeBlock(code='\n'.join(block_lines), language=pending_code_lang, placeholder=current_placeholder))
                
                pending_block_type = None
                pending_code_lang = None
                continue

            if line.startswith('|==='):
                commit_text()
                commit_bullets()
                active_gallery = None
                
                table_lines = []
                i += 1
                while i < len(slide_lines) and not slide_lines[i].strip().startswith('|==='):
                    table_lines.append(slide_lines[i])
                    i += 1
                i += 1
                
                is_csv = False
                has_header = True
                
                if pending_table_attr:
                    is_csv = 'format="csv"' in pending_table_attr or "format='csv'" in pending_table_attr
                    has_header = 'options="header"' in pending_table_attr or 'options=\'header\'' in pending_table_attr or '%header' in pending_table_attr
                else:
                    has_header = True
                
                headers = []
                rows = []
                
                if is_csv:
                    csv_data = [tl.strip() for tl in table_lines if tl.strip()]
                    reader = csv.reader(csv_data)
                    csv_rows = [r for r in reader if r]
                    if csv_rows:
                        if has_header:
                            headers = [c.strip() for c in csv_rows[0]]
                            rows = [[c.strip() for c in r] for r in csv_rows[1:]]
                        else:
                            rows = [[c.strip() for c in r] for r in csv_rows]
                else:
                    psv_rows = []
                    current_row = []
                    for p_line in table_lines:
                        s_line = p_line.strip()
                        if not s_line:
                            if current_row:
                                psv_rows.append(current_row)
                                current_row = []
                        elif s_line.startswith('|'):
                            cells = [c.strip() for c in s_line[1:].split('|')]
                            current_row.extend(cells)
                    if current_row:
                        psv_rows.append(current_row)
                        
                    psv_rows = [r for r in psv_rows if r]
                    
                    if psv_rows:
                        if has_header:
                            headers = psv_rows[0]
                            rows = psv_rows[1:]
                        else:
                            rows = psv_rows
                
                get_target_list().append(Table(headers=headers, rows=rows, placeholder=current_placeholder))
                pending_table_attr = None
                continue

            bullet_match = re.match(r'^(\*+|-+|\.+)\s+(.*)$', line)
            if bullet_match:
                commit_text()
                bullet_chars = bullet_match.group(1)
                text = bullet_match.group(2).strip()
                level = len(bullet_chars) - 1
                current_bullets.append(ListItem(text=text, level=level))
                i += 1
                continue
            else:
                commit_bullets()

            img_match = re.match(r'^image::?([^\[]+)\[(.*?)\]$', line)
            if img_match:
                commit_text()
                img_src = img_match.group(1).strip()
                caption_raw = img_match.group(2).strip()
                caption = caption_raw.split(',')[0].strip() if caption_raw else None
                if not caption:
                    caption = None
                    
                if active_gallery and active_gallery.placeholder == current_placeholder:
                    active_gallery.images.append(Image(source=img_src, caption=caption, placeholder=current_placeholder))
                else:
                    get_target_list().append(Image(source=img_src, caption=caption, placeholder=current_placeholder))
                i += 1
                continue

            current_text.append(normalize_text_line(raw_line))
            i += 1
            
        commit_text()
        commit_bullets()
        
        if active_split:
            raise ValueError(f"Slide '{title}': Unclosed Split detected. A // split was started but never closed with // /split.")
        
        deck.slides.append(slide)

    if deck.slides and deck.slides[0].title and not deck.slides[0].elements and not deck.slides[0].layout_hint:
        deck.slides[0].layout_hint = 'title'

    return deck
