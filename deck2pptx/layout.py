from pptx.util import Inches
from .models import Slide, Gallery, Flow, Image

class Layout:
    def __init__(self, slide_width: int, slide_height: int, title_metrics: dict = None):
        self.slide_width = slide_width
        self.slide_height = slide_height
        
        # Safe margins
        self.margin_x = Inches(0.5)
        self.margin_y = Inches(0.5)
        
        # Title area
        if title_metrics:
            self.title_x = Inches(title_metrics.get('left_inches', 0.5))
            self.title_y = Inches(title_metrics.get('top_inches', 0.5))
            self.title_height = Inches(title_metrics.get('height_inches', 1.2))
            w = title_metrics.get('width_inches', 0)
            self.title_width = Inches(w) if w else (slide_width - (2 * self.margin_x))
        else:
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
