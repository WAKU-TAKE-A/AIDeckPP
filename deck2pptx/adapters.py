from pathlib import Path
from .models import Deck
from .yaml_adapter import load_yaml
from .markdown_adapter import load_markdown

def load_deck(input_path: str | Path, format: str = None) -> Deck:
    input_path = Path(input_path)
    
    if format == 'yaml' or (format is None and input_path.suffix in ('.yaml', '.yml')):
        return load_yaml(input_path)
    elif format == 'markdown' or (format is None and input_path.suffix in ('.md', '.markdown')):
        return load_markdown(input_path)
    else:
        raise ValueError(f"Unsupported format or unknown extension for '{input_path}'")
