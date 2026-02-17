
import pytest
from models import db, Game, Player, GameRound, Trick
from game_engine import GameEngine

def test_troel_forced_lead(app, test_game):
    game, players = test_game
    
    # Setup hands
    hands = {
        str(players[0].id): ['Heart-Ace', 'Diamond-Ace', 'Club-Ace', 'Spade-2', 'Spade-3', 'Spade-4', 'Spade-5', 'Spade-6', 'Spade-7', 'Spade-8', 'Spade-9', 'Spade-10', 'Spade-Jack'],
        str(players[1].id): ['Spade-Ace', 'Heart-2', 'Heart-3', 'Heart-4', 'Heart-5', 'Heart-6', 'Heart-7', 'Heart-8', 'Heart-9', 'Heart-10', 'Heart-Jack', 'Heart-Queen', 'Heart-King'],
        str(players[2].id): ['Club-2', 'Club-3', 'Club-4', 'Club-5', 'Club-6', 'Club-7', 'Club-8', 'Club-9', 'Club-10', 'Club-Jack', 'Club-Queen', 'Club-King', 'Diamond-2'],
        str(players[3].id): ['Diamond-3', 'Diamond-4', 'Diamond-5', 'Diamond-6', 'Diamond-7', 'Diamond-8', 'Diamond-9', 'Diamond-10', 'Diamond-Jack', 'Diamond-Queen', 'Diamond-King', 'Club-5', 'Club-6']
    }
    
    # Create round
    round_num = game.current_round + 1
    round = GameRound(
        game_id=game.id,
        round_number=round_num,
        dealer_position=3,
        hands=hands,
        phase='playing',
        winning_bid='Troel',
        bidder_id=players[0].id,
        partner_id=players[1].id,
        trump_card='Spade-Ace',
        trump_suit='Spade',
        current_trick=0
    )
    db.session.add(round)
    game.current_round = round_num
    db.session.commit()
    
    # Create trick
    trick = Trick(round_id=round.id, trick_number=0, leader_id=players[1].id, cards_played=[])
    db.session.add(trick)
    db.session.commit()
    
    # Refetch
    engine = GameEngine(game.id)
    partner_id = players[1].id
    
    # 2. Verify valid cards for partner (leader)
    current_round_from_engine = engine.get_current_round()
    assert current_round_from_engine is not None
    print(f"DEBUG: engine round phase={current_round_from_engine.phase}, bid={current_round_from_engine.winning_bid}")
    
    valid_cards = engine.get_valid_cards(partner_id)
    print(f"DEBUG: valid_cards={valid_cards}")
    assert len(valid_cards) == 1
    assert valid_cards[0] == 'Spade-Ace'
    
    # 3. Verify playing another card fails
    result = engine.play_card(partner_id, 'Heart-2')
    assert 'error' in result
    
    # 4. Verify playing the correct card succeeds
    result = engine.play_card(partner_id, 'Spade-Ace')
    assert result['status'] == 'success'
