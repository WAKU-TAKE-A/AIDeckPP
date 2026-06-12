import yaml
from pathlib import Path
from .models import Deck, Slide, Text, BulletList, Image, Table, Gallery, Flow, FlowNode, FlowEdge

def load_yaml(file_path: str | Path) -> Deck:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    deck = Deck(
        title=data.get('title'),
        orientation=data.get('orientation', 'landscape'),
        theme=data.get('theme', 'default')
    )
    for slide_data in data.get('slides', []):
        slide = Slide(
            title=slide_data.get('title', ''),
            subtitle=slide_data.get('subtitle'),
            notes=slide_data.get('notes'),
            layout_hint=slide_data.get('layout_hint')
        )
        
        for elem_data in slide_data.get('elements', []):
            if 'text' in elem_data:
                slide.elements.append(Text(content=elem_data['text']))
            elif 'bullet_list' in elem_data:
                slide.elements.append(BulletList(items=elem_data['bullet_list']))
            elif 'image' in elem_data:
                slide.elements.append(Image(source=elem_data['image']))
            elif 'table' in elem_data:
                table_data = elem_data['table']
                slide.elements.append(Table(
                    headers=table_data.get('headers', []),
                    rows=table_data.get('rows', [])
                ))
            elif 'gallery' in elem_data:
                gallery_data = elem_data['gallery']
                images = [Image(source=img) for img in gallery_data.get('images', [])]
                slide.elements.append(Gallery(images=images))
            elif 'flow' in elem_data:
                flow_data = elem_data['flow']
                nodes = [FlowNode(id=n['id'], label=n['label']) for n in flow_data.get('nodes', [])]
                edges = [FlowEdge(from_node=e['from'], to_node=e['to']) for e in flow_data.get('edges', [])]
                slide.elements.append(Flow(
                    direction=flow_data.get('direction', 'horizontal'),
                    nodes=nodes,
                    edges=edges
                ))
        deck.slides.append(slide)
    
    return deck
