import pytest
from pathlib import Path
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE, MSO_SHAPE
from pptx.util import Inches
from deck2pptx.adapters import load_deck
from deck2pptx.renderer import render_deck

def run_pptx_readback(tmp_path, sample_path):
    if not sample_path.exists():
        pytest.skip(f"{sample_path} not found")
        
    deck = load_deck(sample_path)
    out_path = tmp_path / f'{sample_path.name}.pptx'
    
    # Build
    render_deck(deck, out_path, base_dir=sample_path.parent)
    
    assert out_path.exists()
    
    # Readback
    prs = Presentation(str(out_path))
    assert len(prs.slides) == 5
    
    texts = [shape.text for slide in prs.slides for shape in slide.shapes if getattr(shape, 'has_text_frame', False) and shape.text]
    
    assert any("Business Strategy 2026" in t for t in texts)
    assert any("Our approach focuses on the following key areas:" in t for t in texts)
    
    # Verify Gallery slide (slide index 2)
    gallery_slide = prs.slides[2]
    picture_shapes = [shape for shape in gallery_slide.shapes if shape.shape_type == MSO_SHAPE_TYPE.PICTURE]
    assert len(picture_shapes) == 3
    
    # Check horizontal flow
    flow_slide = prs.slides[3]
    auto_shapes = [shape for shape in flow_slide.shapes if shape.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE]
    rectangles = [shape for shape in auto_shapes if shape.auto_shape_type == MSO_SHAPE.RECTANGLE]
    assert len(rectangles) == 3
    
    # Check vertical flow
    vflow_slide = prs.slides[4]
    auto_shapes_v = [shape for shape in vflow_slide.shapes if shape.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE]
    rectangles_v = [shape for shape in auto_shapes_v if shape.auto_shape_type == MSO_SHAPE.RECTANGLE]
    assert len(rectangles_v) == 3

def test_pptx_readback_yaml(tmp_path):
    run_pptx_readback(tmp_path, Path('examples/sample.deck.yaml'))

def test_pptx_readback_markdown(tmp_path):
    run_pptx_readback(tmp_path, Path('examples/sample.md'))
        
def test_reordered_flow_readback(tmp_path):
    sample_path = Path('tests/fixtures/reordered_flow.deck.yaml')
    if not sample_path.exists():
        pytest.skip("reordered_flow.deck.yaml not found")
        
    deck = load_deck(sample_path)
    out_path = tmp_path / 'reordered.pptx'
    
    render_deck(deck, out_path, base_dir=sample_path.parent)
    
    prs = Presentation(str(out_path))
    slide = prs.slides[0]
    
    auto_shapes = [shape for shape in slide.shapes if shape.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE]
    arrows = [shape for shape in auto_shapes if shape.auto_shape_type in (
        MSO_SHAPE.RIGHT_ARROW, MSO_SHAPE.DOWN_ARROW, MSO_SHAPE.LEFT_ARROW, MSO_SHAPE.UP_ARROW
    )]
    
    # 3 edges defined in reordered_flow.deck.yaml
    assert len(arrows) == 3
