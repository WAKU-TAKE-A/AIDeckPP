from pptx.util import Inches
from .models import Slide, Gallery, Flow, Image

class Layout:
    def __init__(self, slide_width: int, slide_height: int):
        self.slide_width = slide_width
        self.slide_height = slide_height
        
        # Safe margins
        self.margin_x = Inches(0.5)
        self.margin_y = Inches(0.5)
        
        # Title area
        self.title_x = self.margin_x
        self.title_y = self.margin_y
        self.title_width = slide_width - (2 * self.margin_x)
        self.title_height = Inches(1.2)
        
        # Content area
        self.content_x = self.margin_x
        self.content_y = self.title_y + self.title_height + Inches(0.2)
        self.content_width = self.title_width
        self.content_height = slide_height - self.content_y - self.margin_y

def get_slide_layout_type(slide: Slide) -> str:
    if slide.layout_hint:
        return slide.layout_hint
        
    if not slide.elements:
        return "title" if slide.subtitle else "content"
        
    # Heuristics based on content
    for elem in slide.elements:
        if isinstance(elem, Gallery):
            return "gallery"
        elif isinstance(elem, Flow):
            return "flow"
            
    if len(slide.elements) == 1 and isinstance(slide.elements[0], Image):
        return "image_only"
        
    return "content"
