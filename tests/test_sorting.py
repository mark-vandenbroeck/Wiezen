
import pytest
from game_engine import GameEngine

def test_sort_cards_alternating_colors():
    # Mix of colors: Hearts (Red), Spades (Black), Diamonds (Red), Clubs (Black)
    hand = [
        "Card-Heart-Ace", "Card-Spade-King", "Card-Diamond-Queen", "Card-Club-Jack",
        "Heart-10", "Spade-9", "Diamond-8", "Club-7"
    ]
    # Note: the actual input format seems to be "Suit-Rank" based on game_engine.py
    # Let me re-check the format: split('-')
    hand = [
        "Harten-Ace", "Schuppen-King", "Ruiten-Queen", "Klaveren-Jack",
        "Harten-10", "Schuppen-9", "Ruiten-8", "Klaveren-7"
    ]
    
    sorted_hand = GameEngine.sort_cards(hand)
    
    # Expected order: Red, Black, Red, Black (or vice versa if counts differ)
    # Harten (R), Schuppen (B), Ruiten (R), Klaveren (B)
    # Ranks should be descending within suit
    
    # Verify suits alternate or follow the interleaved order
    def get_color(card):
        suit = card.split('-')[0]
        if suit in ['Harten', 'Heart', 'Ruiten', 'Diamond']: return 'Red'
        return 'Black'
    
    colors = [get_color(c) for c in sorted_hand]
    
    # In this case all 4 are present, so it should be Red, Black, Red, Black ...
    # but the logic groups by suit. So it should be All Hearts, then All Spades, then All Diamonds, then All Clubs
    # check that the suits themselves alternate colors
    suits_in_order = []
    for c in sorted_hand:
        s = c.split('-')[0]
        if not suits_in_order or suits_in_order[-1] != s:
            suits_in_order.append(s)
            
    color_order = [get_color(f"{s}-Ace") for s in suits_in_order]
    
    # Check for alternation
    for i in range(len(color_order) - 1):
        assert color_order[i] != color_order[i+1], f"Suits did not alternate: {suits_in_order}"

def test_sort_cards_missing_suit():
    # Harten (R), Ruiten (R), Schuppen (B) -> Harten (R), Schuppen (B), Ruiten (R)
    hand = ["Harten-Ace", "Ruiten-King", "Schuppen-Queen"]
    sorted_hand = GameEngine.sort_cards(hand)
    
    # Correct order should be Harten, Schuppen, Ruiten (alternating)
    suits = []
    for c in sorted_hand:
        s = c.split('-')[0]
        if not suits or suits[-1] != s:
            suits.append(s)
    
    assert suits == ["Harten", "Schuppen", "Ruiten"]

def test_sort_cards_ranks():
    # Same suit, different ranks
    hand = ["Harten-10", "Harten-Ace", "Harten-7"]
    sorted_hand = GameEngine.sort_cards(hand)
    
    # Must be Ace, 10, 7
    assert sorted_hand == ["Harten-Ace", "Harten-10", "Harten-7"]

def test_sort_cards_more_blacks():
    # 2 blacks, 1 red -> Black, Red, Black
    hand = ["Klaveren-Ace", "Schuppen-Ace", "Harten-Ace"]
    sorted_hand = GameEngine.sort_cards(hand)
    
    suits = []
    for c in sorted_hand:
        s = c.split('-')[0]
        if not suits or suits[-1] != s:
            suits.append(s)
            
    assert suits == ["Klaveren", "Harten", "Schuppen"] or suits == ["Schuppen", "Harten", "Klaveren"]

if __name__ == "__main__":
    # Quick manual check
    hand = ["Harten-Ace", "Schuppen-King", "Ruiten-Queen", "Klaveren-Jack"]
    print(f"Input: {hand}")
    print(f"Sorted: {GameEngine.sort_cards(hand)}")
