import unittest
from ai_player import AIPlayer
from arch.cards.cards import Card
from arch.cards.suits import Suit
from arch.cards.ranks import Rank

class TestAIStrategy(unittest.TestCase):
    def setUp(self):
        self.ai_medium = AIPlayer(difficulty='medium')
        self.ai_hard = AIPlayer(difficulty='hard')

    def test_medium_losing_follow_suit(self):
        """Test that medium AI plays lowest card when following suit but can't win"""
        hand = [
            Card(Suit.Club, Rank.Ace),
            Card(Suit.Club, Rank.Five),
            Card(Suit.Club, Rank.Two)
        ]
        # Opponent led 7 Clubs, someone played 10 Clubs
        current_trick = [
            (1, Card(Suit.Club, Rank.Seven)),
            (2, Card(Suit.Club, Rank.Ten))
        ]
        trump_suit = Suit.Heart
        led_suit = Suit.Club
        
        # Someone already played Ace of Clubs in a previous trick (mocking via played_cards if hard, 
        # but here we just test that it plays lowest if it can't win the current trick)
        
        # If teammate is NOT winning, and AI has higher but chooses to win or lose.
        # Wait, if it has Ace, it SHOULD win. Let's test when it CAN'T win.
        
        hand_weak = [
            Card(Suit.Club, Rank.Nine),
            Card(Suit.Club, Rank.Five),
            Card(Suit.Club, Rank.Two)
        ]
        # Opponent played Ace of Clubs
        current_trick_lost = [
            (1, Card(Suit.Club, Rank.Ace))
        ]
        
        selected = self.ai_medium.select_card(hand_weak, current_trick_lost, trump_suit, led_suit)
        self.assertEqual(selected.rank, Rank.Two, "Should play lowest card when it can't win")

    def test_medium_wasting_trump(self):
        """Test that medium AI doesn't waste a low trump if it can't overtrump"""
        hand = [
            Card(Suit.Heart, Rank.Five), # Trump
            Card(Suit.Club, Rank.Ace),
            Card(Suit.Club, Rank.Two)
        ]
        # Opponent led 10 Spades, someone trumped with Jack Hearts
        current_trick = [
            (1, Card(Suit.Spade, Rank.Ten)),
            (2, Card(Suit.Heart, Rank.Jack))
        ]
        trump_suit = Suit.Heart
        led_suit = Suit.Spade # AI has no Spades
        
        # AI has no Spades, can trump or discard.
        # It has 5 Hearts, but Jack Hearts is already winning.
        # It should NOT play 5 Hearts, but instead discard lowest card (2 Clubs).
        
        ai_hand = [
            Card(Suit.Heart, Rank.Five),
            Card(Suit.Diamond, Rank.Ace),
            Card(Suit.Diamond, Rank.Two)
        ]
        
        selected = self.ai_medium.select_card(ai_hand, current_trick, trump_suit, led_suit)
        self.assertEqual(selected.suit, Suit.Diamond)
        self.assertEqual(selected.rank, Rank.Two, "Should discard lowest card instead of wasting a low trump")

    def test_hard_losing_follow_suit(self):
        """Test that hard AI plays lowest card when following suit but can't win"""
        hand = [
            Card(Suit.Club, Rank.King),
            Card(Suit.Club, Rank.Five),
            Card(Suit.Club, Rank.Two)
        ]
        # Opponent played Ace of Clubs
        current_trick = [
            (1, Card(Suit.Club, Rank.Ace))
        ]
        trump_suit = Suit.Heart
        led_suit = Suit.Club
        
        selected = self.ai_hard.select_card(hand, current_trick, trump_suit, led_suit)
        self.assertEqual(selected.rank, Rank.Two, "Hard AI should play lowest card when it can't win")

    def test_hard_overtrumping(self):
        """Test that hard AI only trumps if it can win"""
        hand = [
            Card(Suit.Heart, Rank.Five), # Trump
            Card(Suit.Club, Rank.Ace),
            Card(Suit.Club, Rank.Two)
        ]
        # Opponent led 10 Spades, someone trumped with Jack Hearts
        current_trick = [
            (1, Card(Suit.Spade, Rank.Ten)),
            (2, Card(Suit.Heart, Rank.Jack))
        ]
        trump_suit = Suit.Heart
        led_suit = Suit.Spade
        
        ai_hand = [
            Card(Suit.Heart, Rank.Five),
            Card(Suit.Diamond, Rank.Ace),
            Card(Suit.Diamond, Rank.Two)
        ]
        
        selected = self.ai_hard.select_card(ai_hand, current_trick, trump_suit, led_suit)
        self.assertEqual(selected.suit, Suit.Diamond)
        self.assertEqual(selected.rank, Rank.Two, "Hard AI should not waste a low trump")

if __name__ == '__main__':
    unittest.main()
