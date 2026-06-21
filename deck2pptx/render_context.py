from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional
from .theme import Theme
from .layout import Layout
from .models import Deck

@dataclass
class SlideContext:
    slide: Any
    theme: Theme
    deck: Deck
    base_dir: Path
    layout: Layout
    find_placeholder: Callable[[Optional[str]], Any]
    calibrated_metrics: dict = field(default_factory=dict)
    level_fonts: dict = field(default_factory=dict)
