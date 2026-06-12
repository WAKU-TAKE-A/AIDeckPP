from dataclasses import dataclass, field
from typing import List, Optional, Union

@dataclass
class Text:
    content: str

@dataclass
class BulletList:
    items: List[str]

@dataclass
class Image:
    source: str

@dataclass
class Table:
    headers: List[str]
    rows: List[List[str]]

@dataclass
class Gallery:
    images: List[Image]

@dataclass
class FlowNode:
    id: str
    label: str

@dataclass
class FlowEdge:
    from_node: str
    to_node: str

@dataclass
class Flow:
    direction: str  # 'horizontal' or 'vertical'
    nodes: List[FlowNode]
    edges: List[FlowEdge]

Element = Union[Text, BulletList, Image, Table, Gallery, Flow]

@dataclass
class Slide:
    title: str
    subtitle: Optional[str] = None
    notes: Optional[str] = None
    layout_hint: Optional[str] = None
    elements: List[Element] = field(default_factory=list)

@dataclass
class Deck:
    title: Optional[str] = None
    orientation: str = "landscape"
    theme: str = "default"
    slides: List[Slide] = field(default_factory=list)
