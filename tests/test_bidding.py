
import pytest
from models import db, Game, Player, GameRound, Trick
from game_engine import GameEngine
from sqlalchemy.orm.attributes import flag_modified

def test_overbidding_on_high_contract(app, test_game):
    game, players = test_game
    engine = GameEngine(game.id)
    
    # Start a round
    round = engine.start_new_round()
    
    # If Troel was triggered, bidding is skipped. Let's force it back to bidding for the test
    # Or better, just recreate the round without Troel check if possible
    round.phase = 'bidding'
    round.winning_bid = None
    db.session.commit()

    # Player 1 (index 0) bids Abondance
    bidder = engine.get_current_bidder()
    assert bidder is not None, f"Phase is {round.phase}, bids: {round.bids}"
    
    result1 = engine.process_bid(bidder.id, 'Abondance')
    assert result1['status'] == 'bid_recorded'
    
    # Verify phase is still 'bidding'
    round = engine.get_current_round()
    assert round.phase == 'bidding'
    
    # 2. Next bidder bids Solo Slim
    next_bidder = engine.get_current_bidder()
    assert next_bidder.id != bidder.id
    result2 = engine.process_bid(next_bidder.id, 'Solo Slim')
    assert result2['status'] == 'bid_recorded'
    
    # Still bidding
    assert round.phase == 'bidding'
    
    # 3. Third bidder passes
    p3 = engine.get_current_bidder()
    engine.process_bid(p3.id, 'Pas')
    
    # 4. Fourth bidder passes
    p4 = engine.get_current_bidder()
    result4 = engine.process_bid(p4.id, 'Pas')
    
    # Now it should be won by Solo Slim
    assert result4['status'] == 'bid_won'
    assert result4['bid'] == 'Solo Slim'
    
    round = engine.get_current_round()
    assert round.winning_bid == 'Solo Slim'
    assert round.bidder_id == next_bidder.id
    assert round.phase == 'playing'

def test_hierarchy_validation(app, test_game):
    game, players = test_game
    engine = GameEngine(game.id)
    round = engine.start_new_round()
    round.phase = 'bidding'
    round.winning_bid = None
    db.session.commit()
    
    bidder1 = engine.get_current_bidder()
    assert bidder1 is not None
    engine.process_bid(bidder1.id, 'Abondance')
    
    # Next bidder tries to bid something lower, like Vraag
    bidder2 = engine.get_current_bidder()
    print(f"DEBUG: bidder2: {bidder2}, phase: {engine.get_current_round().phase}")
    assert bidder2 is not None
    result = engine.process_bid(bidder2.id, 'Vraag')
    
    assert 'error' in result
    assert 'Cannot bid Vraag after higher bid' in result['error']
