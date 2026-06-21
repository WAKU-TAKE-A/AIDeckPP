from pptx.util import Pt
from pptx.dml.color import RGBColor

class Theme:
    def __init__(self, name: str = "default"):
        self.name = name
        
        # Simple modern business palette
        self.color_primary = RGBColor(0x0F, 0x4C, 0x81)    # Classic Blue
        self.color_text = RGBColor(0x33, 0x33, 0x33)       # Dark Gray
        self.color_text_light = RGBColor(0x66, 0x66, 0x66) # Medium Gray
        self.color_background = RGBColor(0xFF, 0xFF, 0xFF) # White
        self.color_accent = RGBColor(0x00, 0xA8, 0x6B)     # Jade
        self.color_surface = RGBColor(0xF5, 0xF7, 0xFA)    # Light surface
        self.color_border = RGBColor(0xCC, 0xD3, 0xDC)     # Soft border
        self.color_flow_fill = RGBColor(0xEF, 0xF6, 0xFF)  # Pale blue
        self.color_flow_line = RGBColor(0x25, 0x63, 0xEB)  # Clear blue
        self.color_flow_text = RGBColor(0x1E, 0x3A, 0x8A)  # Deep blue
        
        # Typography
        self.font_name = "Calibri" # Usually safe on most systems
        self.size_title = Pt(22)
        self.size_subtitle = Pt(20)
        self.size_body = Pt(20)
        self.size_body_semi_small = Pt(18)
        self.size_body_small = Pt(16)
        self.size_body_extra_small = Pt(14)
