"""
Game Engine for Wiezen
Orchestrates game flow and integrates with database
"""

import random
from models import db, Game, Player, GameRound, Trick, Score
from sqlalchemy.orm.attributes import flag_modified
from arch.cards.deck import Deck
from arch.cards.cards import Card
from arch.cards.suits import Suit, suits
from arch.cards.ranks import Rank, ranks
from ai_player import AIPlayer


class GameEngine:
    """Manages game state and flow"""
    
    def __init__(self, game_id):
        """Initialize game engine for a specific game"""
        self.game_id = game_id
        self.game = Game.query.get(game_id)
        if not self.game:
            raise ValueError(f"Game {game_id} not found")
    
    @staticmethod
    def create_new_game(player_name="Jij", debug_mode=False, ai_difficulties=None):
        """
        Create a new game
        
        Args:
            player_name: Name for human player
            debug_mode: Enable debug mode to show all cards
            ai_difficulties: List of 3 difficulty levels for AI players
        
        Returns:
            Game object
        """
        if ai_difficulties is None:
            ai_difficulties = ['easy', 'medium', 'hard']
        
        # Create game
        game = Game(debug_mode=debug_mode)
        db.session.add(game)
        db.session.flush()  # Get game ID
        
        # Create players
        player_names = [player_name, 'AI Links', 'AI Boven', 'AI Rechts']
        positions = [0, 1, 2, 3]  # bottom, left, top, right
        
        for i, (name, position) in enumerate(zip(player_names, positions)):
            is_human = (i == 0)
            ai_diff = None if is_human else ai_difficulties[i - 1]
            
            player = Player(
                game_id=game.id,
                name=name,
                position=position,
                is_human=is_human,
                ai_difficulty=ai_diff
            )
            db.session.add(player)
        
        db.session.commit()
        db.session.commit()
        return game
    
    @staticmethod
    def sort_cards(card_list):
        """
        Sort a list of card names (Suit-Rank)
        Order: Suit (Harten, Klaveren, Ruiten, Schuppen/Spaden), then Rank (High to Low)
        """
        suit_order = {
            'Harten': 0, 'Heart': 0,
            'Klaveren': 1, 'Club': 1, 
            'Ruiten': 2, 'Diamond': 2,
            'Schuppen': 3, 'Spade': 3
        }
        
        rank_order = {
            'ace': 14, 'aas': 14,
            'king': 13, 'heer': 13,
            'queen': 12, 'dame': 12,
            'jack': 11, 'boer': 11,
            '10': 10, '9': 9, '8': 8, '7': 7, 
            '6': 6, '5': 5, '4': 4, '3': 3, '2': 2
        }
        
        def sort_key(card_name):
            try:
                suit, rank = card_name.split('-')
                s_val = suit_order.get(suit, 99)
                r_val = rank_order.get(rank.lower(), 0)
                return (s_val, -r_val) # Ascending suit, Descending rank
            except:
                return (99, 0)
                
        return sorted(card_list, key=sort_key)
    
    def start_new_round(self):
        """Start a new round with traditional dealing logic"""
        # Determine dealer
        dealer_position = self.game.current_round % 4
        
        # Traditional deck handling
        if self.game.current_round == 0 or not self.game.deck_order:
            # First round: random shuffle
            deck = Deck.full_deck()
            deck.shuffle()
            self.game.deck_order = [f"{c.suit.name}-{c.rank.name}" for c in deck.cards]
            db.session.commit()
        else:
            # Subsequent rounds: use current order and cut
            cards = []
            from arch.cards.suits import suit_name, suits
            from arch.cards.ranks import rank_name, ranks
            
            # Create reverse maps
            rev_suit = {name: s for s, name in suit_name.items()}
            rev_rank = {name: r for r, name in rank_name.items()}
            
            for c_name in self.game.deck_order:
                suit_n, rank_n = c_name.split('-')
                cards.append(Card(rev_suit[suit_n], rev_rank[rank_n]))
            deck = Deck(cards)
            
        # Cut the deck (aflangen)
        deck.aflangen()
        
        # Get trump card (last card)
        trump_card = deck.laatste()
        trump_suit = trump_card.suit.name
        
        # Deal cards in traditional 4-4-5 pattern
        players = Player.query.filter_by(game_id=self.game_id).order_by(Player.position).all()
        hands = {player.id: [] for player in players}
        
        # Pattern: 4, 4, 5. Start from player after dealer
        dealer_idx = dealer_position # Assuming position 0,1,2,3
        
        for amount in [4, 4, 5]:
            for offset in range(1, 5):
                target_pos = (dealer_idx + offset) % 4
                target_player = next(p for p in players if p.position == target_pos)
                for _ in range(amount):
                    card = deck.take_first()
                    hands[target_player.id].append(f"{card.suit.name}-{card.rank.name}")
        
        # Create round
        game_round = GameRound(
            game_id=self.game_id,
            round_number=self.game.current_round + 1,
            dealer_position=dealer_position,
            trump_suit=trump_suit,
            trump_card=f"{trump_card.suit.name}-{trump_card.rank.name}",
            phase='bidding',
            hands=hands
        )
        db.session.add(game_round)
        db.session.flush()

        # Check for Troel
        troel_caller_id = None
        aces_count = 0
        for pid, hand in hands.items():
            aces = [c for c in hand if 'ace' in c.lower() or 'aas' in c.lower()]
            if len(aces) >= 3:
                troel_caller_id = int(pid)
                aces_count = len(aces)
                break
        
        if troel_caller_id:
            partner_id = None
            final_trump_suit = None
            
            if aces_count == 3:
                # Find the player with the 4th Ace
                for pid, hand in hands.items():
                    if int(pid) == troel_caller_id:
                        continue
                    for card_name in hand:
                        if 'ace' in card_name.lower() or 'aas' in card_name.lower():
                            partner_id = int(pid)
                            final_trump_suit = self._parse_suit(card_name.split('-')[0]).name
                            partner_card = card_name
                            break
                    if partner_id: break
            else: # 4 Aces
                final_trump_suit = Suit.Heart.name
                heart_ranks = [Rank.King, Rank.Queen, Rank.Jack, Rank.Ten, Rank.Nine, Rank.Eight, Rank.Seven, Rank.Six, Rank.Five, Rank.Four, Rank.Three, Rank.Two]
                partner_card = None
                for rank in heart_ranks:
                    for pid, hand in hands.items():
                        if int(pid) == troel_caller_id: continue
                        for card_name in hand:
                            s = self._parse_suit(card_name.split('-')[0])
                            r = self._parse_rank(card_name.split('-')[1])
                            if s == Suit.Heart and r == rank:
                                partner_id = int(pid)
                                partner_card = card_name
                                break
                        if partner_id: break
                    if partner_id: break
            
            if partner_id:
                game_round.phase = 'playing'
                game_round.winning_bid = 'Troel'
                game_round.bidder_id = troel_caller_id
                game_round.partner_id = partner_id
                game_round.trump_suit = final_trump_suit
                game_round.trump_card = partner_card
                game_round.current_trick = 0
                
                # Partner leads first trick
                first_trick = Trick(
                    round_id=game_round.id,
                    trick_number=0,
                    leader_id=partner_id,
                    cards_played=[]
                )
                db.session.add(first_trick)
        
        self.game.current_round += 1
        db.session.commit()
        
        return game_round
    
    def get_current_round(self):
        """Get current round"""
        return GameRound.query.filter_by(
            game_id=self.game_id,
            round_number=self.game.current_round
        ).first()

    def _get_bid_value(self, bid):
        """Helper to get numeric value of a bid for hierarchy"""
        if bid == 'Pas': return 0
        if bid == 'Vraag': return 1
        if bid == 'Mee': return 1
        if bid == 'Abondance': return 2
        if bid == 'Miserie': return 3
        if bid == 'Open Miserie': return 4
        if bid == 'Solo Slim': return 5
        return 0

    def get_current_bidder(self):
        """Get the player whose turn it is to bid"""
        current_round = self.get_current_round()
        if not current_round:
            return None
            
        if current_round.phase == 'choosing_alleen':
            return Player.query.get(current_round.bidder_id)
            
        if current_round.phase != 'bidding':
            return None
            
        bids = current_round.bids or []
        if len(bids) >= 4:
            return None
            
        dealer_pos = current_round.dealer_position
        next_pos = (dealer_pos + 1 + len(bids)) % 4
        
        return Player.query.filter_by(game_id=self.game_id, position=next_pos).first()

    def process_bid(self, player_id, bid):
        """
        Process a player's bid
        
        Args:
            player_id: ID of player making bid
            bid: Bid string ('Pas', 'Vraag', 'Mee', 'Solo Slim', 'Miserie', 'Alleen')
        
        Returns:
            dict with bidding status
        """
        current_round = self.get_current_round()
        if not current_round or current_round.phase not in ['bidding', 'choosing_alleen']:
            return {'error': 'Not in bidding phase'}
            
        # Validate turn
        current_bidder = self.get_current_bidder()
        if not current_bidder or current_bidder.id != player_id:
            return {'error': f'Not your turn (Waiting for {current_bidder.name if current_bidder else "None"})'}
        
        if current_round.phase == 'choosing_alleen':
            if bid not in ['Alleen', 'Pas']:
                return {'error': 'Must choose Alleen or Pas'}
            
            if bid == 'Alleen':
                current_round.winning_bid = 'Alleen'
                current_round.phase = 'playing'
                current_round.current_trick = 0
                # Initialize first trick
                first_trick = Trick(
                    round_id=current_round.id,
                    trick_number=0,
                    leader_id=self._get_expected_leader_id(current_round, 0),
                    cards_played=[]
                )
                db.session.add(first_trick)
                db.session.commit()
                return {'status': 'bid_won', 'bid': 'Alleen'}
            else: # Pas (Alleen was rejected)
                current_round.phase = 'completed'
                current_round.winning_bid = 'Pas'
                db.session.commit()
                return {'status': 'all_passed'}

        # Validate bid hierarchy
        if bid != 'Pas':
            bids = current_round.bids or []
            max_val = 0
            has_vraag = False
            for b in bids:
                val = self._get_bid_value(b['bid'])
                if val > max_val:
                    max_val = val
                if b['bid'] == 'Vraag':
                    has_vraag = True
            
            curr_val = self._get_bid_value(bid)
            
            if bid == 'Mee':
                if not has_vraag:
                    return {'error': 'Cannot bid Mee without Vraag'}
                if max_val > 1:
                     return {'error': 'Cannot bid Mee after higher bid'}
            elif bid == 'Vraag' and has_vraag:
                 return {'error': 'Vraag already bid'}
            elif curr_val < max_val:
                return {'error': f'Cannot bid {bid} after higher bid'}

        # Store bid
        bids = list(current_round.bids) if current_round.bids else []
        bids.append({'player_id': player_id, 'bid': bid})
        current_round.bids = bids
        flag_modified(current_round, "bids")
        db.session.commit()
        
        # Instant wins
        if bid in ['Solo Slim', 'Miserie', 'Abondance', 'Open Miserie']:
            current_round.winning_bid = bid
            current_round.bidder_id = player_id
            current_round.phase = 'playing'
            current_round.current_trick = 0
            
            # Initialize first trick
            first_trick = Trick(
                round_id=current_round.id,
                trick_number=0,
                leader_id=self._get_expected_leader_id(current_round, 0),
                cards_played=[]
            )
            db.session.add(first_trick)
            db.session.commit()
            return {'status': 'bid_won', 'bid': bid}
            
        # Check if bidding is complete (4 bids)
        if len(bids) == 4:
            # Count Non-Pass
            real_bids = [b for b in bids if b['bid'] != 'Pas']
            
            if not real_bids:
                # All passed
                current_round.phase = 'completed'
                current_round.winning_bid = 'Pas'
                db.session.commit()
                return {'status': 'all_passed'}
            
            # Find the highest bid
            max_bid_info = real_bids[0]
            max_val = self._get_bid_value(max_bid_info['bid'])
            for b in real_bids:
                if self._get_bid_value(b['bid']) > max_val:
                    max_bid_info = b
                    max_val = self._get_bid_value(b['bid'])

            # Case: Vraag was highest but not joined
            if max_bid_info['bid'] == 'Vraag' and not any(b['bid'] == 'Mee' for b in bids):
                current_round.phase = 'choosing_alleen'
                current_round.bidder_id = max_bid_info['player_id']
                db.session.commit()
                return {'status': 'waiting_for_alleen', 'bidder_id': current_round.bidder_id}

            # Case: Vraag joined by Mee
            if any(b['bid'] == 'Mee' for b in bids):
                vraag_info = next(b for b in bids if b['bid'] == 'Vraag')
                mee_info = next(b for b in bids if b['bid'] == 'Mee')
                current_round.winning_bid = 'Vraag'
                current_round.bidder_id = vraag_info['player_id']
                current_round.partner_id = mee_info['player_id']
                current_round.phase = 'playing'
            else:
                # Any other high bid (Miserie or Solo Slim handled above but safely fallback)
                current_round.winning_bid = max_bid_info['bid']
                current_round.bidder_id = max_bid_info['player_id']
                current_round.phase = 'playing'
            
            current_round.current_trick = 0
            first_trick = Trick(
                round_id=current_round.id,
                trick_number=0,
                leader_id=self._get_expected_leader_id(current_round, 0),
                cards_played=[]
            )
            db.session.add(first_trick)
            db.session.commit()
            
            return {
                'status': 'bid_won', 
                'bid': current_round.winning_bid, 
                'bidder_id': current_round.bidder_id
            }

        return {'status': 'bid_recorded', 'next_bidder': self.get_current_bidder().id if self.get_current_bidder() else None}
    
    def _get_expected_leader_id(self, current_round, trick_number):
        """Determine who should be the leader for a given trick number"""
        if trick_number == 0:
            # First trick: player after dealer
            next_pos = (current_round.dealer_position + 1) % 4
            leader = Player.query.filter_by(game_id=self.game_id, position=next_pos).first()
            if leader:
                return leader.id
            # Absolute fallback
            return Player.query.filter_by(game_id=self.game_id).first().id
        else:
            # Subsequent tricks: winner of previous trick
            prev_trick = Trick.query.filter_by(
                round_id=current_round.id,
                trick_number=trick_number - 1
            ).first()
            
            if prev_trick and prev_trick.winner_id:
                return prev_trick.winner_id
            
            # If previous winner not found, fallback to previous leader (safety)
            if prev_trick and prev_trick.leader_id:
                return prev_trick.leader_id
                
            # Nuclear fallback: player after dealer
            next_pos = (current_round.dealer_position + 1) % 4
            leader = Player.query.filter_by(game_id=self.game_id, position=next_pos).first()
            return leader.id if leader else None

    def _get_current_turn_player_id(self, current_round, trick=None):
        """Determine whose turn it is to play"""
        if not trick:
            trick = Trick.query.filter_by(
                round_id=current_round.id,
                trick_number=current_round.current_trick
            ).first()
            
        if not trick:
            return self._get_expected_leader_id(current_round, current_round.current_trick)

        # Determine from trick
        leader = Player.query.get(trick.leader_id)
        current_count = len(trick.cards_played)
        expected_pos = (leader.position + current_count) % 4
        expected_player = Player.query.filter_by(game_id=self.game_id, position=expected_pos).first()
        return expected_player.id

    def get_valid_cards(self, player_id):
        """
        Get valid cards that a player can play
        
        Args:
            player_id: Player ID
        
        Returns:
            List of valid card names
        """
        current_round = self.get_current_round()
        if not current_round or current_round.phase != 'playing':
            return []
        
        # Check turn
        current_turn_id = self._get_current_turn_player_id(current_round)
        if player_id != current_turn_id:
            return []
            
        # Get player's hand
        hand_names = current_round.hands.get(str(player_id), [])
        hand = [self._parse_card(name) for name in hand_names]
        
        # Get current trick
        current_trick_num = current_round.current_trick
        trick = Trick.query.filter_by(
            round_id=current_round.id,
            trick_number=current_trick_num
        ).first()
        
        # If no trick exists yet, we assume leading
        if not trick or not trick.cards_played:
            # Leading, all cards valid
            return hand_names
        
        # Determine led suit
        led_card_name = trick.cards_played[0]['card_name']
        led_card = self._parse_card(led_card_name)
        led_suit = led_card.suit
        
        # Must follow suit if possible
        same_suit = [name for name, card in zip(hand_names, hand) if card.suit == led_suit]
        if same_suit:
            return same_suit
        
        # Can't follow suit, all cards valid
        return hand_names
    
    def play_card(self, player_id, card_name):
        """
        Play a card
        
        Args:
            player_id: Player ID
            card_name: Card name (e.g., "Heart-Ace")
        
        Returns:
            dict with play result
        """
        current_round = self.get_current_round()
        if not current_round or current_round.phase != 'playing':
            return {'error': 'Not in playing phase'}
        
        # Validate card is in hand
        hand = current_round.hands.get(str(player_id), [])
        if card_name not in hand:
            return {'error': 'Card not in hand'}
        
        # Validate card is legal
        valid_cards = self.get_valid_cards(player_id)
        if card_name not in valid_cards:
            return {'error': 'Invalid card play'}
        
        # Remove card from hand
        # IMPORTANT: Use a new list to ensure change detection or flag modified
        new_hand = list(hand)
        new_hand.remove(card_name)
        
        # Update hands dict - need to copy dict to trigger update?
        # Or use flag_modified explicitly
        current_round.hands[str(player_id)] = new_hand
        flag_modified(current_round, 'hands')
        
        # Get or create current trick
        trick = Trick.query.filter_by(
            round_id=current_round.id,
            trick_number=current_round.current_trick
        ).first()
        
        if not trick:
            trick = Trick(
                round_id=current_round.id,
                trick_number=current_round.current_trick,
                leader_id=self._get_expected_leader_id(current_round, current_round.current_trick),
                cards_played=[]
            )
            db.session.add(trick)
        
        # Add card to trick
        cards_played = list(trick.cards_played or [])
        cards_played.append({
            'player_id': player_id,
            'card_name': card_name,
            'order': len(cards_played)
        })
        trick.cards_played = cards_played
        flag_modified(trick, 'cards_played')
        
        # Check if trick is complete
        if len(cards_played) == 4:
            # Determine winner
            winner_id = self._determine_trick_winner(
                cards_played,
                current_round.trump_suit
            )
            trick.winner_id = winner_id
            
            # Early termination for Miserie (if bidder wins a trick, they lose)
            if current_round.winning_bid in ['Miserie', 'Open Miserie'] and winner_id == current_round.bidder_id:
                current_round.phase = 'completed'
                self._calculate_scores(current_round)
                db.session.commit()
                return {
                    'status': 'success',
                    'trick_complete': True,
                    'round_complete': True
                }
            
            # Move to next trick
            current_round.current_trick += 1
            
            # Check if round is complete
            if current_round.current_trick >= 13:
                current_round.phase = 'completed'
                self._calculate_scores(current_round)
            else:
                # Create next trick with previous winner as leader
                # This ensures checkTurnAndAct finds the correct leader
                next_trick = Trick(
                    round_id=current_round.id,
                    trick_number=current_round.current_trick,
                    leader_id=winner_id,
                    cards_played=[]
                )
                db.session.add(next_trick)
        
        db.session.commit()
        
        return {
            'status': 'success',
            'trick_complete': len(cards_played) == 4,
            'round_complete': current_round.phase == 'completed'
        }


    
    def get_ai_bid(self, player_id):
        """Get a bid string from an AI player"""
        current_round = self.get_current_round()
        if not current_round:
            return None
            
        player = Player.query.get(player_id)
        if not player or player.is_human:
            return None
            
        ai = AIPlayer(difficulty=player.ai_difficulty)
        
        if current_round.phase == 'choosing_alleen':
            # AI chooses whether to go Alleen after rejected Vraag
            hand_names = current_round.hands.get(str(player_id), [])
            hand = [self._parse_card(name) for name in hand_names]
            trump_card = self._parse_card(current_round.trump_card)
            bid = ai.choose_alleen_or_pas(hand, trump_card)
            return bid

        # Normal bidding
        hand_names = current_round.hands.get(str(player_id), [])
        hand = [self._parse_card(name) for name in hand_names]
        
        # Parse previous bids
        prev_bids = [b['bid'] for b in (current_round.bids or [])]
        trump_card = self._parse_card(current_round.trump_card)
        
        # Position is relative to dealer
        position = (player.position - current_round.dealer_position - 1) % 4
        
        bid = ai.make_bid(hand, trump_card, position, prev_bids)
        
        # If Solo Slim or Abondance is bid by AI, they pick the best suit
        if bid in ['Solo Slim', 'Abondance']:
            # Find suit with most cards
            suit_counts = {}
            for card in hand:
                suit_counts[card.suit] = suit_counts.get(card.suit, 0) + 1
            best_suit = max(suit_counts, key=suit_counts.get)
            current_round.trump_suit = best_suit.name
            current_round.trump_card = f"{best_suit.name}-Ace"
            
        return bid
    
    def get_ai_card(self, player_id):
        """Get AI player's card selection"""
        player = Player.query.get(player_id)
        if not player or player.is_human:
            return None
        
        current_round = self.get_current_round()
        hand_names = current_round.hands.get(str(player_id), [])
        hand = [self._parse_card(name) for name in hand_names]
        
        # Get current trick
        trick = Trick.query.filter_by(
            round_id=current_round.id,
            trick_number=current_round.current_trick
        ).first()
        
        current_trick = []
        led_suit = None
        if trick and trick.cards_played:
            for card_play in trick.cards_played:
                card = self._parse_card(card_play['card_name'])
                current_trick.append((card_play['player_id'], card))
            led_suit = current_trick[0][1].suit
        
        trump_suit = self._parse_suit(current_round.trump_suit)
        
        # Determine partners
        partner_ids = []
        if current_round.winning_bid in ['Vraag', 'Troel']:
            if player_id == current_round.bidder_id:
                partner_ids = [current_round.partner_id]
            elif player_id == current_round.partner_id:
                partner_ids = [current_round.bidder_id]
            else:
                # Defenders are partners
                all_ids = [p.id for p in Player.query.filter_by(game_id=self.game_id).all()]
                partner_ids = [pid for pid in all_ids if pid != player_id and pid not in [current_round.bidder_id, current_round.partner_id]]
        else:
            # Solo contracts (Alleen, Abondance, Solo Slim, Miserie)
            if player_id == current_round.bidder_id:
                partner_ids = [] # No partners for attacker
            else:
                # All other players are partners for defenders
                all_ids = [p.id for p in Player.query.filter_by(game_id=self.game_id).all()]
                partner_ids = [pid for pid in all_ids if pid != player_id and pid != current_round.bidder_id]

        try:
            # Calculate context for Hard AI: played cards and player voids
            played_cards = []
            player_voids = {} # {player_id: [suits]}
            
            # Get all completed tricks in this round
            all_tricks = Trick.query.filter(
                Trick.round_id == current_round.id,
                Trick.trick_number <= current_round.current_trick
            ).all()
            
            for t in all_tricks:
                if not t.cards_played:
                    continue
                    
                trick_led_suit = None
                for i, card_play in enumerate(t.cards_played):
                    p_id = card_play['player_id']
                    card_obj = self._parse_card(card_play['card_name'])
                    if not card_obj:
                        continue
                        
                    played_cards.append(card_obj)
                    
                    if i == 0:
                        trick_led_suit = card_obj.suit
                    elif trick_led_suit and card_obj.suit != trick_led_suit:
                        # Player did not follow suit -> they are void in that suit
                        if p_id not in player_voids:
                            player_voids[p_id] = []
                        if trick_led_suit not in player_voids[p_id]:
                            player_voids[p_id].append(trick_led_suit)

            # Determine if partner is winning
            is_partner_winning = False
            if current_trick:
                # Filter out None cards from current_trick for safety
                clean_trick_cards = [cp for cp in trick.cards_played if self._parse_card(cp['card_name'])]
                if clean_trick_cards:
                    winning_id = self._determine_trick_winner(clean_trick_cards, current_round.trump_suit)
                    if winning_id in partner_ids:
                        is_partner_winning = True

            ai = AIPlayer(difficulty=player.ai_difficulty)
            card = ai.select_card(
                hand, 
                current_trick, 
                trump_suit, 
                led_suit, 
                is_partner_winning=is_partner_winning, 
                is_miserie=is_miserie,
                played_cards=played_cards,
                player_voids=player_voids,
                partner_ids=partner_ids
            )
        except Exception as e:
            # Fallback to basic AI selection to prevent game freeze
            # In a real app we would log this to a proper logger
            ai = AIPlayer(difficulty='medium') # Fallback to medium
            card = ai.select_card(hand, current_trick, trump_suit, led_suit, is_partner_winning=False)
        
        # Find the card name in the original hand list that matches the selected card
        for name, hand_card in zip(hand_names, hand):
            if hand_card.suit == card.suit and hand_card.rank == card.rank:
                return name
        
        # Fallback
        return f"{card.suit.name}-{card.rank.name}"
    
    def _parse_card(self, card_name):
        """Parse card name to Card object"""
        suit_name, rank_name = card_name.split('-')
        suit = self._parse_suit(suit_name)
        rank = self._parse_rank(rank_name)
        return Card(suit, rank)
    
    def _parse_suit(self, suit_name):
        """Parse suit name to Suit object with Dutch support"""
        suit_map = {
            'Harten': Suit.Heart, 'Heart': Suit.Heart, 'Hearts': Suit.Heart,
            'Klaveren': Suit.Club, 'Club': Suit.Club, 'Clubs': Suit.Club,
            'Ruiten': Suit.Diamond, 'Diamond': Suit.Diamond, 'Diamonds': Suit.Diamond,
            'Schuppen': Suit.Spade, 'Spade': Suit.Spade, 'Spades': Suit.Spade, 'Schoppen': Suit.Spade
        }
        
        # Direct map check (case insensitive)
        for key, val in suit_map.items():
            if key.lower() == suit_name.lower():
                return val
        
        # Fallback to direct attribute
        if hasattr(Suit, suit_name.title()):
            return getattr(Suit, suit_name.title())
            
        return Suit.Unknown

    def _parse_rank(self, rank_name):
        """Parse rank name to Rank object with Dutch support"""
        rank_map = {
            'aas': Rank.Ace, 'ace': Rank.Ace,
            'heer': Rank.King, 'king': Rank.King,
            'dame': Rank.Queen, 'queen': Rank.Queen,
            'boer': Rank.Jack, 'jack': Rank.Jack,
            '10': Rank.Ten, 'ten': Rank.Ten,
            '9': Rank.Nine, 'nine': Rank.Nine,
            '8': Rank.Eight, 'eight': Rank.Eight,
            '7': Rank.Seven, 'seven': Rank.Seven,
            '6': Rank.Six, 'six': Rank.Six,
            '5': Rank.Five, 'five': Rank.Five,
            '4': Rank.Four, 'four': Rank.Four,
            '3': Rank.Three, 'three': Rank.Three,
            '2': Rank.Two, 'two': Rank.Two
        }
        
        if rank_name.lower() in rank_map:
            return rank_map[rank_name.lower()]
        
        # Try title case
        if hasattr(Rank, rank_name.title()):
            return getattr(Rank, rank_name.title())
            
        return Rank.Unknown
    
    def _determine_trick_winner(self, cards_played, trump_suit_name):
        """Determine winner of a trick"""
        trump_suit = self._parse_suit(trump_suit_name)
        
        led_card = self._parse_card(cards_played[0]['card_name'])
        led_suit = led_card.suit
        
        winning_play = cards_played[0]
        winning_card = led_card
        
        for play in cards_played[1:]:
            card = self._parse_card(play['card_name'])
            
            # Trump beats non-trump
            if card.suit == trump_suit and winning_card.suit != trump_suit:
                winning_play = play
                winning_card = card
            # Higher trump beats lower trump
            elif card.suit == trump_suit and winning_card.suit == trump_suit:
                if card.rank.value > winning_card.rank.value:
                    winning_play = play
                    winning_card = card
            # Higher card of led suit
            elif card.suit == led_suit and winning_card.suit == led_suit:
                if card.rank.value > winning_card.rank.value:
                    winning_play = play
                    winning_card = card
        
        return winning_play['player_id']
    
    def _calculate_scores(self, game_round):
        """Calculate and store zero-sum scores for completed round"""
        # Get all tricks
        tricks = Trick.query.filter_by(round_id=game_round.id).all()
        
        # Count tricks won by each player
        trick_counts = {}
        for trick in tricks:
            if trick.winner_id:
                trick_counts[trick.winner_id] = trick_counts.get(trick.winner_id, 0) + 1
        
        # Distinguish attackers and defenders
        if not game_round.bidder_id:
            print(f"WARNING: No bidder_id for round {game_round.id}, skipping scoring")
            return
            
        attacking_ids = [game_round.bidder_id]
        if game_round.partner_id:
            attacking_ids.append(game_round.partner_id)
            
        players = Player.query.filter_by(game_id=self.game_id).all()
        player_ids = [p.id for p in players]
        defending_ids = [pid for pid in player_ids if pid not in attacking_ids]
        
        # Total tricks won by attacking side
        attack_tricks = sum(trick_counts.get(pid, 0) for pid in attacking_ids)
        
        # Calculate base points per contract
        points_per_defender = 0
        
        if game_round.winning_bid in ['Vraag', 'Troel']:
            # Base 2 points for 8 tricks, +1 for each extra
            if attack_tricks >= 8:
                points_per_defender = 2 + (attack_tricks - 8)
            else:
                points_per_defender = -(2 + (8 - attack_tricks))
                
        elif game_round.winning_bid == 'Alleen':
            # Alleen: Win 5+ tricks
            if attack_tricks >= 5:
                points_per_defender = 2 + (attack_tricks - 5)
            else:
                points_per_defender = -(2 + (5 - attack_tricks))
                
        elif game_round.winning_bid == 'Abondance':
            # Abondance: 8 points per defender, 9 tricks target
            # Overslagen niet geteld
            target_tricks = 9
            base_points = 8
            if attack_tricks >= 9:
                points_per_defender = base_points
            else:
                points_per_defender = -base_points
                
        elif game_round.winning_bid == 'Solo Slim':
            # Solo Slim: All 13 tricks
            if attack_tricks == 13:
                points_per_defender = 24
            else:
                points_per_defender = -24
                
        elif game_round.winning_bid in ['Miserie', 'Open Miserie']:
        # Miserie: Win 0 tricks
        # Open Miserie: same goal, but 16 pts
            base_points = 12 if game_round.winning_bid == 'Miserie' else 16
            if attack_tricks == 0:
                points_per_defender = base_points 
            else:
                points_per_defender = -base_points
    
        # Calculate total points to transfer
        # If attacker wins, they get points from EACH defender
        total_transfer = points_per_defender * len(defending_ids)
        
        # Distribute scores (Zero-sum)
        final_scores = {pid: 0 for pid in player_ids}
        
        # Attacking side split the total transfer
        for pid in attacking_ids:
            final_scores[pid] = total_transfer / len(attacking_ids)
            
        # Each defender pays/gets the base points
        for pid in defending_ids:
            final_scores[pid] = -points_per_defender
            
        # Store to database
        for pid, pts in final_scores.items():
            score = Score(
                game_id=self.game_id,
                player_id=pid,
                round_number=game_round.round_number,
                points=int(pts)
            )
            db.session.add(score)
        
        db.session.commit()
    
        # After scoring, collect all cards for traditional dealing
        # They are collected in the order they were played in the tricks
        all_cards = []
        tricks = Trick.query.filter_by(round_id=game_round.id).order_by(Trick.trick_number).all()
        for trick in tricks:
            if trick.cards_played:
                for play in trick.cards_played:
                    all_cards.append(play['card_name'])
                
        # Update game deck order for next round
        self.game.deck_order = all_cards
        flag_modified(self.game, "deck_order")
        db.session.commit()
