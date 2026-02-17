
import pytest
from arch.cards.suits import Suit
from arch.cards.ranks import Rank
from arch.cards.cards import Card
from ai_player import AIPlayer

def test_calculate_card_probabilities():
    ai = AIPlayer(difficulty='hard')
    
    # Hand with some high cards
    hand = [
        Card(Suit.Spade, Rank.Ace),
        Card(Suit.Spade, Rank.King),
        Card(Suit.Heart, Rank.Two),
    ]
    
    # No cards played yet
    probs = ai.calculate_card_probabilities(hand, [], {}, Suit.Diamond)
    
    # Ace of Spade should have 1.0 prob since it's the highest and no trumps played yet (in a leading scenario)
    # Actually, my simplified formula might give less than 1.0 if trumps are still out.
    # Let's check the logic.
    
    assert probs[Card(Suit.Spade, Rank.Ace).name] > 0.6
    assert probs[Card(Suit.Spade, Rank.King).name] < probs[Card(Suit.Spade, Rank.Ace).name]
    assert probs[Card(Suit.Heart, Rank.Two).name] < 0.4

def test_simulate_hand_performance():
    ai = AIPlayer(difficulty='hard')
    
    # Very strong hand
    strong_hand = [
        Card(Suit.Spade, Rank.Ace), Card(Suit.Spade, Rank.King), Card(Suit.Spade, Rank.Queen),
        Card(Suit.Heart, Rank.Ace), Card(Suit.Heart, Rank.King), Card(Suit.Heart, Rank.Queen),
        Card(Suit.Diamond, Rank.Ace), Card(Suit.Diamond, Rank.King), Card(Suit.Diamond, Rank.Queen),
        Card(Suit.Club, Rank.Ace), Card(Suit.Club, Rank.King), Card(Suit.Club, Rank.Queen),
        Card(Suit.Spade, Rank.Jack)
    ]
    
    avg_tricks = ai._simulate_hand_performance(strong_hand, Suit.Spade, simulations=20)
    assert avg_tricks > 10
    
    # Very weak hand
    weak_hand = [
        Card(Suit.Spade, Rank.Two), Card(Suit.Spade, Rank.Three), Card(Suit.Spade, Rank.Four),
        Card(Suit.Heart, Rank.Two), Card(Suit.Heart, Rank.Three), Card(Suit.Heart, Rank.Four),
        Card(Suit.Diamond, Rank.Two), Card(Suit.Diamond, Rank.Three), Card(Suit.Diamond, Rank.Four),
        Card(Suit.Club, Rank.Two), Card(Suit.Club, Rank.Three), Card(Suit.Club, Rank.Four),
        Card(Suit.Club, Rank.Five)
    ]
    
    avg_tricks_weak = ai._simulate_hand_performance(weak_hand, Suit.Spade, simulations=20)
    assert avg_tricks_weak < 3

def test_hard_bid_logic():
    ai = AIPlayer(difficulty='hard')
    
    # Hand that should definitely Solo Slim
    perfect_hand = [Card(Suit.Spade, rank) for rank in Rank]
    bid = ai.make_bid(perfect_hand, Card(Suit.Spade, Rank.Two), 0, [])
    assert bid == 'Solo Slim'
    
    # Very weak hand should Miserie
    weak_hand = [
        Card(Suit.Spade, Rank.Two), Card(Suit.Heart, Rank.Two), Card(Suit.Club, Rank.Two), Card(Suit.Diamond, Rank.Two),
        Card(Suit.Spade, Rank.Three), Card(Suit.Heart, Rank.Three), Card(Suit.Club, Rank.Three), Card(Suit.Diamond, Rank.Three),
        Card(Suit.Spade, Rank.Four), Card(Suit.Heart, Rank.Four), Card(Suit.Club, Rank.Four), Card(Suit.Diamond, Rank.Four),
        Card(Suit.Spade, Rank.Five)
    ]
    bid_weak = ai.make_bid(weak_hand, Card(Suit.Diamond, Rank.Ace), 0, [])
    assert bid_weak == 'Miserie'
