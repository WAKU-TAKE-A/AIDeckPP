import subprocess
import tempfile
import shutil
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import MSO_AUTO_SIZE

from .models import Text, BulletList, Image, Table, Gallery, Flow, Split, CodeBlock, Mermaid, Tree, Comparison, Timeline
from .text_utils import count_rendered_lines

ELEMENT_GAP = Inches(0.15)          # uniform gap between consecutive elements
_TEXT_LINE_HEIGHT = Inches(0.35)    # estimated height per wrapped line of body text
_BULLET_LINE_HEIGHT = Inches(0.32)  # estimated height per bullet item line
_TEXT_MIN_HEIGHT = Inches(0.4)      # minimum text box height (approx 1 line)
_BULLET_MIN_HEIGHT = Inches(0.8)    # minimum bullet list height

def _get_font_size(level_fonts, theme, level=0):
    fs = 24.0 if level == 0 else 18.0
    if theme and hasattr(theme, 'size_body'):
        fs = theme.size_body.pt
    if level_fonts and level in level_fonts:
        fs = level_fonts[level]
    return fs

def _get_calibrated_metrics(fs, calibrated_metrics):
    if not calibrated_metrics:
        return None, None
    if fs in calibrated_metrics:
        return calibrated_metrics[fs]['height'], calibrated_metrics[fs]['cpi']
    
    # Find closest
    closest_fs = min(calibrated_metrics.keys(), key=lambda k: abs(k - fs))
    ref = calibrated_metrics[closest_fs]
    ratio = fs / closest_fs
    return ref['height'] * ratio, ref['cpi'] * (1.0 / ratio)

def _estimate_element_height(element, content_width, calibrated_metrics=None, theme=None, level_fonts=None, calibrated_heights=None):
    """Return estimated rendered height (EMU) for an element."""
    if getattr(element, 'height_hint', None) is not None:
        return element.height_hint

    if isinstance(element, Text):
        fs = _get_font_size(level_fonts, theme, 0)
        calib_h, calib_cpi = _get_calibrated_metrics(fs, calibrated_metrics)
        
        line_height = calib_h
        if not line_height and calibrated_heights:
            line_height = calibrated_heights.get(0)
            
        if line_height:
            if calib_cpi:
                width_inches = content_width / 914400.0 if content_width else 10.0
                chars_per_line = max(1, int(width_inches * calib_cpi))
            else:
                chars_per_line = 60
            estimated_lines = element.content.count('\n') + 1 + len(element.content) // chars_per_line
            return max(_TEXT_MIN_HEIGHT, estimated_lines * line_height + Inches(0.1))
        else:
            estimated_lines = element.content.count('\n') + 1 + len(element.content) // 60
            return max(_TEXT_MIN_HEIGHT, estimated_lines * _TEXT_LINE_HEIGHT)

    if isinstance(element, BulletList):
        from .models import ListItem
        total_h = 0
        has_calib = bool(calibrated_metrics) or bool(calibrated_heights)
        for item in element.items:
            lvl = item.level if isinstance(item, ListItem) else 0
            text = item.text if isinstance(item, ListItem) else str(item)
            fs = _get_font_size(level_fonts, theme, lvl)
            calib_h, calib_cpi = _get_calibrated_metrics(fs, calibrated_metrics)
            
            line_height = calib_h
            if not line_height and calibrated_heights:
                line_height = calibrated_heights.get(lvl)

            if line_height:
                if calib_cpi:
                    width_inches = content_width / 914400.0 if content_width else 10.0
                    indent_inches = 0.2 + (lvl * 0.2)
                    avail_width = max(1.0, width_inches - indent_inches)
                    chars_per_line = max(1, int(avail_width * calib_cpi))
                else:
                    chars_per_line = 50
                lines = text.count('\n') + 1 + len(text) // chars_per_line
                total_h += lines * line_height
            else:
                weight = 1.0 if lvl == 0 else 0.8
                total_h += weight * _BULLET_LINE_HEIGHT
        return max(_BULLET_MIN_HEIGHT, total_h + Inches(0.1))

    if isinstance(element, CodeBlock):
        lines = len(element.code.splitlines()) if element.code else 1
        box_h = Inches(max(1.0, lines * 0.25 + 0.2))
        caption_h = Inches(0.4) if (getattr(element, 'caption', None) or getattr(element, 'language', None)) else 0
        return caption_h + box_h
        
    if isinstance(element, Mermaid):
        from . import mermaid_handler
        if mermaid_handler.has_mermaid_cli():
            return getattr(element, 'height_hint', None) or Inches(3.0)
        else:
            lines = len(element.code.splitlines()) if element.code else 1
            box_h = Inches(max(1.0, lines * 0.25 + 0.2))
            return box_h

    if isinstance(element, Tree):
        def count_leaves(node):
            if not node.children:
                return 1
            return sum(count_leaves(child) for child in node.children)
        leaf_count = count_leaves(element.root)
        node_height = Inches(0.4)
        vertical_gap = Inches(0.15)
        return max(Inches(1.0), leaf_count * node_height + (leaf_count - 1) * vertical_gap)

    if isinstance(element, Timeline):
        return len(element.events) * Inches(0.8)

    if isinstance(element, Comparison):
        num_cols = len(element.columns)
        if num_cols == 0:
            return Inches(1.0)
        col_width_inches = (content_width / 914400.0 if content_width else 10.0) / num_cols
        
        calib_h = None
        calib_cpi = None
        body_font_size = theme.size_body if theme else 18
        if calibrated_metrics and body_font_size in calibrated_metrics:
            calib_h = calibrated_metrics[body_font_size].get('height')
            calib_cpi = calibrated_metrics[body_font_size].get('cpi')
        
        chars_per_line = max(1, int(col_width_inches * calib_cpi)) if calib_cpi else 30
        line_height = calib_h if calib_h else _TEXT_LINE_HEIGHT

        max_lines = 0
        for col in element.columns:
            lines = 1  # for the label
            for item in col.items:
                lines += count_rendered_lines(item, chars_per_line)
            if lines > max_lines:
                max_lines = lines
                
        title_h = Inches(0.5) if element.title else 0
        return title_h + (max_lines * line_height) + Inches(0.1)

    if isinstance(element, Flow):
        if getattr(element, 'direction', 'horizontal') == 'vertical':
            count = len(element.items) if hasattr(element, 'items') else 1
            return max(Inches(1.0), count * Inches(0.5) + max(0, count - 1) * Inches(0.4))
        else:
            return Inches(1.5)

    # Image, Gallery, Table, Split:
    # height depends on runtime data — caller handles these separately.
    return Inches(1.0)
def get_adjusted_height(elements_list, current_idx, total_bottom_y, current_y, content_width, calibrated_metrics=None, theme=None, level_fonts=None, calibrated_heights=None):
    """Estimate available height for elements_list[current_idx]."""
    remaining_h = total_bottom_y - current_y
    if remaining_h < Inches(1): remaining_h = Inches(1)

    from . import mermaid_handler
    has_mmdc = mermaid_handler.has_mermaid_cli()

    # Reserve height for all text-like elements that come AFTER the current one.
    future_elements = elements_list[current_idx + 1:]
    reserved_text_h = sum(
        _estimate_element_height(e, content_width, calibrated_metrics, theme, level_fonts, calibrated_heights) + ELEMENT_GAP
        for e in future_elements
        if getattr(e, 'placeholder', None) is None and (
            isinstance(e, (Text, BulletList, CodeBlock, Tree, Comparison, Timeline)) or (isinstance(e, Mermaid) and not has_mmdc)
        )
    )

    remaining_imgs = sum(
        1 for e in elements_list[current_idx:]
        if isinstance(e, (Image, Gallery, Split, Table)) or (isinstance(e, Mermaid) and has_mmdc)
    )

    available_img_h = remaining_h - reserved_text_h
    if available_img_h < Inches(1): available_img_h = Inches(1)

    current_element = elements_list[current_idx]
    if (isinstance(current_element, (Image, Gallery, Split, Table)) or (isinstance(current_element, Mermaid) and has_mmdc)) and remaining_imgs > 0:
        return available_img_h / remaining_imgs
    else:
        return remaining_h

def calibrate_line_heights(deck, theme):
    soffice_cmd = None
    if shutil.which("soffice"):
        soffice_cmd = "soffice"
    else:
        win_path = r"C:\Program Files\LibreOffice\program\soffice.exe"
        if Path(win_path).exists():
            soffice_cmd = win_path
    
    if not soffice_cmd:
        return {}

    prs = Presentation()
    blank_layout = prs.slide_layouts[6] if len(prs.slide_layouts) > 6 else prs.slide_layouts[0]
    slide = prs.slides.add_slide(blank_layout)

    default_sizes = [24, 20, 18, 16, 14]
    
    for level in range(5):
        fs = getattr(deck, f"font_size_l{level}", None)
        if fs is None:
            fs = default_sizes[level]
        
        txBox = slide.shapes.add_textbox(Inches(0), Inches(level * 1.5), Inches(20), Inches(1))
        tf = txBox.text_frame
        tf.auto_size = MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT
        tf.word_wrap = False
        
        lines_text = "\n".join([f"Line {i+1}" for i in range(10)])
        tf.text = lines_text
        
        for p in tf.paragraphs:
            p.font.name = theme.font_name if theme and theme.font_name else "Arial"
            p.font.size = Pt(fs)

    temp_dir = tempfile.mkdtemp()
    try:
        input_pptx = Path(temp_dir) / "calib_input.pptx"
        prs.save(str(input_pptx))
        
        output_temp_dir = Path(tempfile.mkdtemp())
        try:
            subprocess.run([soffice_cmd, "--headless", "--convert-to", "pptx", str(input_pptx), "--outdir", str(output_temp_dir)], check=True, capture_output=True)
            output_pptx = output_temp_dir / "calib_input.pptx"
            if not output_pptx.exists():
                return {}
            
            prs_out = Presentation(str(output_pptx))
            slide_out = prs_out.slides[0]
            
            result = {}
            for level, shape in enumerate(slide_out.shapes):
                if shape.height == Inches(1):
                    return {}
                result[level] = shape.height / 10.0
                
            return result
        finally:
            shutil.rmtree(output_temp_dir, ignore_errors=True)
    except Exception as e:
        print(f"Calibration error: {e}")
        return {}
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def extract_template_metrics(slide) -> tuple[dict, dict]:
    """Extracts calibration metrics from a slide."""
    calibrated_metrics = {}
    title_metrics = {
        'font_size_pt': 20.0,
        'height_inches': 1.2,
        'top_inches': 0.5,
        'left_inches': 0.5,
        'width_inches': 0.0
    }
    title_found = False
    
    for shape in slide.shapes:
        if shape.is_placeholder and shape.placeholder_format.type in (1, 3):
            if not title_found:
                title_metrics['height_inches'] = shape.height / 914400.0 if shape.height else 1.2
                title_metrics['top_inches'] = shape.top / 914400.0 if shape.top else 0.5
                title_metrics['left_inches'] = shape.left / 914400.0 if shape.left else 0.5
                title_metrics['width_inches'] = shape.width / 914400.0 if shape.width else 0.0
                
                if shape.has_text_frame:
                    for p in shape.text_frame.paragraphs:
                        for run in p.runs:
                            if run.font.size:
                                title_metrics['font_size_pt'] = run.font.size.pt
                                break
                        if title_metrics['font_size_pt'] != 20.0: break
                title_found = True
            continue
            
        if shape.has_text_frame:
            text = shape.text
            lines = text.count('\n') + text.count('\x0b') + 1
            if lines >= 3:
                font_size_pt = None
                for p in shape.text_frame.paragraphs:
                    for run in p.runs:
                        if run.font.size:
                            font_size_pt = run.font.size.pt
                            break
                    if font_size_pt: break
                
                if font_size_pt:
                    height_per_line = int(font_size_pt * 15240)
                    first_para_text = shape.text_frame.paragraphs[0].text.split('\x0b')[0]
                    cpi = len(first_para_text) / (shape.width / 914400.0) if shape.width else 60.0 / 6.0
                    calibrated_metrics[font_size_pt] = {
                        'shape_name': shape.name,
                        'font_size_pt': font_size_pt,
                        'lines': lines,
                        'chars_per_line': len(first_para_text),
                        'box_width_inches': shape.width / 914400.0 if shape.width else 0.0,
                        'box_height_inches': shape.height / 914400.0 if shape.height else 0.0,
                        'cpi': cpi,
                        'height': height_per_line
                    }
    return calibrated_metrics, title_metrics

