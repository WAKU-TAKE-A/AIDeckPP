from pptx.util import Pt
from ..render_context import SlideContext

def render(element, ctx: SlideContext, x, y, w, h) -> float:
    rows = len(element.rows) + 1 if element.headers else len(element.rows)
    cols = len(element.headers) if element.headers else (len(element.rows[0]) if element.rows else 1)

    ph = ctx.find_placeholder(getattr(element, 'placeholder', None))
    target_x = ph.left if ph else x
    target_y = ph.top if ph else y
    target_w = ph.width if ph else w

    table_shape = ctx.slide.shapes.add_table(rows, cols, target_x, target_y, target_w, ctx.theme.table.placeholder_init_height)
    table = table_shape.table

    # Clear template default style and apply Table Grid style
    try:
        table.style = 'Table Grid'
    except Exception:
        pass

    row_offset = 0
    if element.headers:
        for i, header in enumerate(element.headers):
            cell_obj = table.cell(0, i)
            cell_obj.text = header
            cell_obj.fill.solid()
            cell_obj.fill.fore_color.rgb = ctx.theme.table.header_fill_color
            for p in cell_obj.text_frame.paragraphs:
                p.font.name = ctx.theme.font.name
                p.font.size = ctx.theme.table.header_font_size
                p.font.bold = True
                p.font.color.rgb = ctx.theme.color.text
        row_offset = 1

    for r_idx, row in enumerate(element.rows):
        for c_idx, cell in enumerate(row):
            cell_obj = table.cell(r_idx + row_offset, c_idx)
            cell_obj.text = str(cell)
            cell_obj.fill.solid()
            cell_obj.fill.fore_color.rgb = ctx.theme.color.background
            for p in cell_obj.text_frame.paragraphs:
                p.font.name = ctx.theme.font.name
                p.font.size = ctx.theme.table.cell_font_size
                p.font.color.rgb = ctx.theme.color.text

    if not ph:
        rendered_height = getattr(element, 'height_hint', None)
        if rendered_height is None:
            rendered_height = table_shape.height
        return y + rendered_height + ctx.theme.layout.element_gap
    return y
