from dataclasses import dataclass, field
from typing import List, Optional, Union

@dataclass
class Text:
    content: str
    placeholder: Optional[str] = None
    height_hint: Optional[float] = None

@dataclass
class ListItem:
    text: str
    level: int = 0

@dataclass
class BulletList:
    items: List[Union[str, ListItem]]
    placeholder: Optional[str] = None
    height_hint: Optional[float] = None

@dataclass
class Image:
    source: str
    caption: Optional[str] = None
    placeholder: Optional[str] = None
    height_hint: Optional[float] = None

@dataclass
class Table:
    headers: List[str]
    rows: List[List[str]]
    placeholder: Optional[str] = None
    height_hint: Optional[float] = None

@dataclass
class Gallery:
    images: List[Image]
    rows: Optional[int] = None
    columns: Optional[int] = None
    placeholder: Optional[str] = None
    height_hint: Optional[float] = None

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
    placeholder: Optional[str] = None
    height_hint: Optional[float] = None

@dataclass
class ComparisonColumn:
    label: str
    items: List[str]

@dataclass
class Comparison:
    columns: List[ComparisonColumn]
    title: Optional[str] = None
    placeholder: Optional[str] = None
    height_hint: Optional[float] = None

@dataclass
class TimelineEvent:
    label: str
    title: str
    description: Optional[str] = None

@dataclass
class Timeline:
    events: List[TimelineEvent]
    placeholder: Optional[str] = None
    height_hint: Optional[float] = None

@dataclass
class CodeBlock:
    code: str
    language: Optional[str] = None
    caption: Optional[str] = None
    placeholder: Optional[str] = None
    height_hint: Optional[float] = None

@dataclass
class Mermaid:
    code: str
    placeholder: Optional[str] = None
    height_hint: Optional[float] = None

@dataclass
class TreeNode:
    label: str
    children: List['TreeNode'] = field(default_factory=list)

@dataclass
class Tree:
    root: TreeNode
    placeholder: Optional[str] = None
    height_hint: Optional[float] = None

@dataclass
class Panel:
    title: Optional[str] = None
    elements: List['Element'] = field(default_factory=list)

@dataclass
class Split:
    direction: str
    panels: List[Panel]
    placeholder: Optional[str] = None
    height_hint: Optional[float] = None

@dataclass
class Quote:
    text: str
    placeholder: Optional[str] = None
    height_hint: Optional[float] = None

Element = Union[Text, BulletList, Image, Table, Gallery, Flow, Comparison, Timeline, CodeBlock, Mermaid, Tree, Split, Quote]

@dataclass
class Slide:
    title: str
    subtitle: Optional[str] = None
    notes: Optional[str] = None
    layout_hint: Optional[str] = None
    content_align: Optional[str] = None
    section_no: Optional[str] = None
    level: int = 1
    elements: List[Element] = field(default_factory=list)

@dataclass
class Deck:
    title: Optional[str] = None
    input_format: str = "markdown"
    orientation: str = "landscape"
    theme: str = "default"
    toc: bool = False
    toc_title: Optional[str] = None
    indent: Optional[int] = None
    content_align: Optional[str] = None
    footer: Optional[str] = None
    date: Optional[str] = None
    slides: List[Slide] = field(default_factory=list)
