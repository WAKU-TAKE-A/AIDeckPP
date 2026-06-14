from dataclasses import asdict
from .models import Deck

def inspect_deck(deck: Deck) -> dict:
    return asdict(deck)
