"""
AI Player for Wiezen
Implements rule-based strategies with three difficulty levels
"""

import random
from arch.cards.suits import Suit
from arch.cards.ranks import Rank
from arch.cards.cards import Card


class AIPlayer:
    """AI player with configurable difficulty"""
    
    def __init__(self, difficulty='medium'):
        """
        Initialize AI player
        
        Args:
            difficulty: 'easy', 'medium', or 'hard'
        """
        self.difficulty = difficulty
    
    def make_bid(self, hand, trump_card, position, previous_bids):
        """
        Decide on a bid based on hand strength
        
        Args:
            hand: List of Card objects
            trump_card: The revealed trump card
            position: Player position (0-3)
            previous_bids: List of previous bids in this round
        
        Returns:
            Bid string: 'Pas', 'Vraag', 'Mee', 'Abondance', 'Solo Slim', 'Miserie', 'Open Miserie'
        """
        # Count hand strength
        trump_suit = trump_card.suit
        num_trumps = sum(1 for card in hand if card.suit == trump_suit)
        num_aces = sum(1 for card in hand if card.rank == Rank.Ace)
        num_high_cards = sum(1 for card in hand if card.rank in [Rank.Ace, Rank.King, Rank.Queen])
        
        # Analyze suit distribution for Abondance
        suit_counts = {}
        for suit in [Suit.Heart, Suit.Diamond, Suit.Club, Suit.Spade]:
            suit_counts[suit] = sum(1 for card in hand if card.suit == suit)
        max_suit_len = max(suit_counts.values())
        
        # Check max bid level from previous bids
        max_bid_val = 0
        for bid in previous_bids:
            # We need a way to map bid names to values here too, or just use rank
            val = self._get_bid_value_for_ai(bid)
            if val > max_bid_val:
                max_bid_val = val

        # Check for Open Miserie (very weak hand)
        low_cards = sum(1 for card in hand if card.rank in [Rank.Two, Rank.Three, Rank.Four, Rank.Five])
        is_open_miserie_candidate = (num_high_cards == 0 and num_trumps <= 1 and low_cards >= 9)

        # Check if someone already bid Vraag
        vraag_bid = any(bid == 'Vraag' for bid in previous_bids)
        
        # Difficulty-based decision making
        bid = 'Pas'
        if self.difficulty == 'easy':
            if is_open_miserie_candidate and random.random() < 0.05: bid = 'Open Miserie'
            elif max_suit_len >= 8: bid = 'Abondance'
            else: bid = self._easy_bid(num_trumps, num_aces, num_high_cards, vraag_bid)
        elif self.difficulty == 'hard':
            if is_open_miserie_candidate and random.random() < 0.2: bid = 'Open Miserie'
            else:
                best_suit = max(suit_counts, key=suit_counts.get)
                suit_highs = sum(1 for c in hand if c.suit == best_suit and c.rank in [Rank.Ace, Rank.King])
                if max_suit_len >= 7 and suit_highs >= 1: bid = 'Abondance'
                else: bid = self._hard_bid(hand, trump_suit, num_trumps, num_aces, num_high_cards, vraag_bid)
        else:  # medium
            if is_open_miserie_candidate and random.random() < 0.1: bid = 'Open Miserie'
            elif max_suit_len >= 8: bid = 'Abondance'
            else: bid = self._medium_bid(num_trumps, num_aces, num_high_cards, vraag_bid)

        # Enforce hierarchy: if chosen bid is lower than max, or same but already bid (for level >= 2), return Pas
        if bid != 'Pas':
            bid_val = self._get_bid_value_for_ai(bid)
            if bid_val < max_bid_val:
                return 'Pas'
            if bid_val == max_bid_val and bid_val >= 2:
                # Can't overbid same level
                return 'Pas'
            # Level 1 joins are allowed (Mee after Vraag)
            if bid == 'Vraag' and vraag_bid:
                return 'Pas' # Already bid
            
        return bid

    def _get_bid_value_for_ai(self, bid):
        """Internal helper for AI to know bid strengths"""
        values = {
            'Pas': 0, 'Vraag': 1, 'Mee': 1, 'Alleen': 1,
            'Abondance': 2, 'Miserie': 3, 'Open Miserie': 4, 'Solo Slim': 5
        }
        return values.get(bid, 0)

    def choose_alleen_or_pas(self, hand, trump_card):
        """Decide whether to go Alleen if Vraag wasn't joined"""
        # If we have at least 5 trumps or many high cards, go Alleen
        trump_suit = trump_card.suit
        num_trumps = sum(1 for card in hand if card.suit == trump_suit)
        num_aces = sum(1 for card in hand if card.rank == Rank.Ace)
        
        if num_trumps >= 5 or num_aces >= 3:
            return 'Alleen'
        return 'Pas'
    
    def _easy_bid(self, num_trumps, num_aces, num_high_cards, vraag_bid):
        """Easy AI: Simple random-ish decisions"""
        if vraag_bid and num_trumps >= 3:
            return 'Mee'
        elif num_trumps >= 6 and num_aces >= 1:
            return 'Vraag'
        elif num_trumps >= 11:
            return 'Solo Slim'
        elif random.random() < 0.1:  # 10% chance of random bid
            return random.choice(['Vraag', 'Pas'])
        return 'Pas'
    
    def _medium_bid(self, num_trumps, num_aces, num_high_cards, vraag_bid):
        """Medium AI: Reasonable strategy"""
        # Consider Solo Slim
        if num_trumps >= 10 and num_aces >= 3:
            return 'Solo Slim'
            
        # Consider Mee if someone asked
        if vraag_bid:
            if num_trumps >= 4 or num_aces >= 2:
                return 'Mee'
        
        # Consider Vraag
        if num_trumps >= 5 and num_high_cards >= 5:
            return 'Vraag'
        
        # Consider Miserie (very rare)
        if num_high_cards == 0 and random.random() < 0.05:
            return 'Miserie'
        
        return 'Pas'
    
    def _hard_bid(self, hand, trump_suit, num_trumps, num_aces, num_high_cards, vraag_bid):
        """Hard AI: Advanced strategy with suit analysis"""
        # Consider Solo Slim (near perfect hand)
        if num_trumps >= 9 and num_aces >= 4:
            return 'Solo Slim'
            
        # Analyze suit distribution
        suit_counts = {}
        for suit in [Suit.Heart, Suit.Diamond, Suit.Club, Suit.Spade]:
            suit_counts[suit] = sum(1 for card in hand if card.suit == suit)
        
        # Count winners (Aces and Kings in non-trump suits)
        potential_winners = 0
        for card in hand:
            if card.suit != trump_suit:
                if card.rank == Rank.Ace:
                    potential_winners += 1
                elif card.rank == Rank.King and suit_counts[card.suit] >= 3:
                    potential_winners += 0.5
        
        # Consider Mee strategically
        if vraag_bid:
            if num_trumps >= 4 and (num_aces >= 2 or potential_winners >= 2):
                return 'Mee'
            elif num_trumps >= 5:
                return 'Mee'
        
        # Consider Vraag with good hand
        if num_trumps >= 5 and num_high_cards >= 6:
            return 'Vraag'
        elif num_trumps >= 6 and num_aces >= 1:
            return 'Vraag'
        
        # Consider Miserie with weak hand
        if num_high_cards <= 1 and num_trumps <= 2:
            # Check if we have mostly low cards
            low_cards = sum(1 for card in hand if card.rank in [Rank.Two, Rank.Three, Rank.Four, Rank.Five])
            if low_cards >= 8 and random.random() < 0.15:
                return 'Miserie'
        
        return 'Pas'
    
    def select_card(self, hand, current_trick, trump_suit, led_suit, is_partner_winning=False, is_miserie=False, played_cards=None, player_voids=None, partner_ids=None):
        """
        Select a card to play
        
        Args:
            hand: List of Card objects in player's hand
            current_trick: List of (player_id, Card) tuples played so far
            trump_suit: Current trump suit
            led_suit: Suit that was led (None if leading)
            is_partner_winning: Whether partner is currently winning the trick
            is_miserie: Whether the contract is Miserie (goal: win 0 tricks)
            played_cards: List of Cards already played this round
            player_voids: Dictionary {player_id: [Suits]} of known voids
            partner_ids: List of IDs for current player's teammates
        
        Returns:
            Card to play
        """
        if is_miserie:
            return self._miserie_card_selection(hand, current_trick, trump_suit, led_suit)
            
        if self.difficulty == 'easy':
            return self._easy_card_selection(hand, current_trick, trump_suit, led_suit)
        elif self.difficulty == 'hard':
            return self._hard_card_selection(hand, current_trick, trump_suit, led_suit, is_partner_winning, played_cards, player_voids, partner_ids)
        else:  # medium
            return self._medium_card_selection(hand, current_trick, trump_suit, led_suit, is_partner_winning)

    def _miserie_card_selection(self, hand, current_trick, trump_suit, led_suit):
        """Strategic play for Miserie: AVOD winning tricks"""
        if led_suit is None:
            # Leading: play relatively high card of a "safe" suit?
            # Or just play the lowest card to be safe.
            # Actually, leading a high card might be good if others MUST follow and have higher.
            # But in Wiezen Miserie, usually you want to lead low or "break" a suit.
            # Let's play the lowest card of the longest suit to stay safe.
            suit_counts = {}
            for card in hand:
                suit_counts[card.suit] = suit_counts.get(card.suit, 0) + 1
            
            # Find longest suit
            best_suit = max(suit_counts, key=suit_counts.get)
            suit_cards = [c for c in hand if c.suit == best_suit]
            
            # Lead lowest of that suit
            return min(suit_cards, key=lambda c: c.rank.value)

        # Must follow suit if possible
        same_suit = [card for card in hand if card.suit == led_suit]
        if same_suit:
            # Determine currently winning card in trick
            winning_card = self._get_current_winning_card(current_trick, trump_suit)
            
            # Strategy: play the HIGHEST card that is still LOWER than the winning card
            # This gets rid of high cards safely.
            # If all cards are higher, play the LOWEST card (forced to win or play high).
            
            lower_cards = [c for c in same_suit if c.rank.value < winning_card.rank.value]
            if lower_cards:
                return max(lower_cards, key=lambda c: c.rank.value)
            
            # All cards are higher: forced to play, play lowest to keep better cards for later
            return min(same_suit, key=lambda c: c.rank.value)

        # Can't follow suit: Discard the HIGHEST card in the hand (Aces, Kings)
        # to get rid of dangerous cards.
        return max(hand, key=lambda c: c.rank.value)
    
    def _easy_card_selection(self, hand, current_trick, trump_suit, led_suit):
        """Easy AI: Play first valid card or random"""
        if led_suit is None:
            # Leading: play random card
            return random.choice(hand)
        
        # Must follow suit if possible
        same_suit = [card for card in hand if card.suit == led_suit]
        if same_suit:
            return random.choice(same_suit)
        
        # Can't follow suit: play random
        return random.choice(hand)
    
    def _medium_card_selection(self, hand, current_trick, trump_suit, led_suit, is_partner_winning):
        """Medium AI: Basic strategic play"""
        if led_suit is None:
            # Leading: play high card or trump
            aces = [card for card in hand if card.rank == Rank.Ace]
            if aces:
                return random.choice(aces)
            
            kings = [card for card in hand if card.rank == Rank.King]
            if kings:
                return random.choice(kings)
            
            # Play random card
            return random.choice(hand)
        
        # Must follow suit if possible
        same_suit = [card for card in hand if card.suit == led_suit]
        if same_suit:
            winning_card = self._get_current_winning_card(current_trick, trump_suit)
            if is_partner_winning:
                # Partner winning: play low card
                return min(same_suit, key=lambda c: c.rank.value)
            else:
                # Try to win with lowest winning card
                if winning_card:
                    higher_cards = [card for card in same_suit if card.rank.value > winning_card.rank.value]
                    # If winning card is a trump and we aren't following with a trump, we can't win by following suit
                    if winning_card.suit == trump_suit and led_suit != trump_suit:
                        higher_cards = []
                    
                    if higher_cards:
                        # Play LOWEST winning card
                        return min(higher_cards, key=lambda c: c.rank.value)
                
                # Can't win: play lowest card to save high cards
                return min(same_suit, key=lambda c: c.rank.value)
        
        # Can't follow suit
        trumps = [card for card in hand if card.suit == trump_suit]
        if trumps and not is_partner_winning:
            # Only trump if we can actually win
            winning_card = self._get_current_winning_card(current_trick, trump_suit)
            if winning_card:
                if winning_card.suit == trump_suit:
                    higher_trumps = [card for card in trumps if card.rank.value > winning_card.rank.value]
                    if higher_trumps:
                        return min(higher_trumps, key=lambda c: c.rank.value)
                else:
                    # Any trump wins against non-trump
                    return min(trumps, key=lambda c: c.rank.value)
        
        # Can't win or no trumps: discard lowest card
        return min(hand, key=lambda c: c.rank.value)
    
    def _hard_card_selection(self, hand, current_trick, trump_suit, led_suit, is_partner_winning, played_cards=None, player_voids=None, partner_ids=None):
        """Hard AI: Advanced strategic play with card counting and void tracking"""
        played_cards = played_cards or []
        player_voids = player_voids or {}
        
        # Helper: Is a card a "guaranteed winner" in its suit?
        def is_sure_winner(card):
            if card.rank == Rank.Ace:
                return True
            # Check if all higher cards have been played
            higher_ranks = [r for r in Rank if r.value > card.rank.value]
            for r in higher_ranks:
                higher_card_played = any(c.suit == card.suit and c.rank == r for c in played_cards)
                # Also check if WE have the higher card in hand
                higher_card_in_hand = any(c.suit == card.suit and c.rank == r for c in hand)
                if not (higher_card_played or higher_card_in_hand):
                    return False
            return True

        if led_suit is None:
            # Leading: strategic choice
            
            # 1. Lead "Sure Winners" (Aces or Kings if Ace is gone)
            for card in hand:
                if is_sure_winner(card) and card.suit != trump_suit:
                    return card
            
            # 2. Lead Trump if we have many to clear them
            trumps = [card for card in hand if card.suit == trump_suit]
            if len(trumps) >= 5:
                # Lead a medium/high trump
                return max(trumps, key=lambda c: c.rank.value)
            
            # 3. Void Exploitation: 
            # If an opponent is void in a suit, leading that suit can be good to force them to trump.
            opponent_ids = []
            if partner_ids is not None:
                # We need to know our own ID to be 100% sure, but we can assume anyone NOT in partner_ids 
                # (and not us) is an opponent. However, partner_ids already excludes us.
                opponent_ids = [p_id for p_id in player_voids.keys() if p_id not in partner_ids]
            
            # Analyze suit counts in hand
            suit_counts = {}
            for card in hand:
                suit_counts[card.suit] = suit_counts.get(card.suit, 0) + 1
                
            for suit, count in suit_counts.items():
                if count >= 3 and suit != trump_suit:
                    for opp_id in opponent_ids:
                        if opp_id in player_voids and suit in player_voids[opp_id]:
                            # Opponent is void! Lead a low card of this suit to force them.
                            suit_cards = [c for c in hand if c.suit == suit]
                            return min(suit_cards, key=lambda c: c.rank.value)
            
            # Lead with high card
            high_cards = [card for card in hand if card.rank in [Rank.King, Rank.Queen, Rank.Jack]]
            if high_cards:
                return max(high_cards, key=lambda c: c.rank.value)
            
            return random.choice(hand)
        
        # Must follow suit if possible
        same_suit = [card for card in hand if card.suit == led_suit]
        if same_suit:
            winning_card = self._get_current_winning_card(current_trick, trump_suit)
            
            if is_partner_winning:
                # Partner winning: play lowest card to save high cards
                return min(same_suit, key=lambda c: c.rank.value)
            
            # Opponent is winning
            higher_cards = [card for card in same_suit if card.rank.value > winning_card.rank.value]
            # If winning card is a trump and we aren't following with a trump, we can't win by following suit
            if winning_card and winning_card.suit == trump_suit and led_suit != trump_suit:
                higher_cards = []
                
            # Try to win with lowest winning card, but be smart
            if higher_cards:
                # If we have a choice of winners, use the lowest one
                # UNLESS we want to keep it.
                return min(higher_cards, key=lambda c: c.rank.value)
            
            # Can't win: play lowest
            return min(same_suit, key=lambda c: c.rank.value)
        
        # Can't follow suit
        trumps = [card for card in hand if card.suit == trump_suit]
        if trumps and not is_partner_winning:
            # Trump with lowest trump that wins
            winning_card = self._get_current_winning_card(current_trick, trump_suit)
            if winning_card and winning_card.suit == trump_suit:
                higher_trumps = [card for card in trumps if card.rank.value > winning_card.rank.value]
                if higher_trumps:
                    return min(higher_trumps, key=lambda c: c.rank.value)
            elif winning_card:
                # Winning card is not trump, any trump wins
                return min(trumps, key=lambda c: c.rank.value)
            
            # If we can't overtrump, don't waste a trump unless forced
        
        # Discard lowest non-trump card
        # EXCEPT: discard a suit where we want to become void!
        non_trumps = [card for card in hand if card.suit != trump_suit]
        if non_trumps:
            return min(non_trumps, key=lambda c: c.rank.value)
        
        return min(hand, key=lambda c: c.rank.value)
    
    def _get_current_winning_card(self, current_trick, trump_suit):
        """Determine which card is currently winning the trick"""
        if not current_trick:
            return None
        
        led_suit = current_trick[0][1].suit
        winning_card = current_trick[0][1]
        
        for player_id, card in current_trick[1:]:
            # Trump beats non-trump
            if card.suit == trump_suit and winning_card.suit != trump_suit:
                winning_card = card
            # Higher trump beats lower trump
            elif card.suit == trump_suit and winning_card.suit == trump_suit:
                if card.rank.value > winning_card.rank.value:
                    winning_card = card
            # Higher card of led suit beats lower (if no trumps involved)
            elif card.suit == led_suit and winning_card.suit == led_suit:
                if card.rank.value > winning_card.rank.value:
                    winning_card = card
        
        return winning_card
