
import pytest
from models import db, Game, Player, GameRound, Trick
from game_engine import GameEngine

def test_overbidding_higher_level(app, test_game):
    game, players = test_game
    engine = GameEngine(game.id)
    
    # Setup a round in bidding phase
    round_num = game.current_round + 1
    round = GameRound(
        game_id=game.id,
        round_number=round_num,
        dealer_position=3, 
        hands={},
        phase='bidding'
    )
    db.session.add(round)
    game.current_round = round_num
    db.session.commit()
    
    # 1. Player 1 (pos 0) bids Vraag (Val 1)
    engine.process_bid(players[0].id, 'Vraag')
    
    # 2. Player 2 (pos 1) bids Abondance (Val 2) - Higher, should be allowed
    res = engine.process_bid(players[1].id, 'Abondance')
    assert 'error' not in res
    
    # 3. Player 3 (pos 2) tries to bid Vraag (Val 1) - Lower than current max (2)
    res = engine.process_bid(players[2].id, 'Vraag')
    assert 'error' in res
    
    # 4. Player 3 bids Solo Slim (Val 5) - Much higher, allowed
    res = engine.process_bid(players[2].id, 'Solo Slim')
    assert 'error' not in res
    
    # 5. Player 4 (pos 3) bids Pas
    engine.process_bid(players[3].id, 'Pas')
    
    # Final check: Solo Slim should win
    db.session.refresh(round)
    assert round.winning_bid == 'Solo Slim'
    assert round.bidder_id == players[2].id
    assert round.phase == 'playing'

def test_bidding_hierarchy_winner_determination(app, test_game):
    game, players = test_game
    engine = GameEngine(game.id)
    
    round_num = game.current_round + 1
    round = GameRound(game_id=game.id, round_number=round_num, dealer_position=3, phase='bidding')
    db.session.add(round)
    game.current_round = round_num
    db.session.commit()
    
    engine.process_bid(players[0].id, 'Abondance')
    engine.process_bid(players[1].id, 'Abondance')
    engine.process_bid(players[2].id, 'Pas')
    engine.process_bid(players[3].id, 'Pas')
    
    db.session.refresh(round)
    assert round.winning_bid == 'Abondance'
    assert round.bidder_id == players[0].id

def test_level_1_vraag_mee(app, test_game):
    game, players = test_game
    engine = GameEngine(game.id)
    
    round_num = game.current_round + 1
    round = GameRound(game_id=game.id, round_number=round_num, dealer_position=3, phase='bidding')
    db.session.add(round)
    game.current_round = round_num
    db.session.commit()
    
    engine.process_bid(players[0].id, 'Vraag')
    engine.process_bid(players[1].id, 'Pas')
    engine.process_bid(players[2].id, 'Mee')
    engine.process_bid(players[3].id, 'Pas')
    
    db.session.refresh(round)
    assert round.winning_bid == 'Vraag'
    assert round.bidder_id == players[0].id
    assert round.partner_id == players[2].id

def test_level_1_alleen(app, test_game):
    game, players = test_game
    engine = GameEngine(game.id)
    
    round_num = game.current_round + 1
    round = GameRound(game_id=game.id, round_number=round_num, dealer_position=3, phase='bidding')
    db.session.add(round)
    game.current_round = round_num
    db.session.commit()
    
    engine.process_bid(players[0].id, 'Vraag')
    engine.process_bid(players[1].id, 'Pas')
    engine.process_bid(players[2].id, 'Alleen')
    engine.process_bid(players[3].id, 'Pas')
    
    db.session.refresh(round)
    assert round.winning_bid == 'Alleen'
    assert round.bidder_id == players[2].id

def test_miserie_over_abondance(app, test_game):
    game, players = test_game
    engine = GameEngine(game.id)
    
    round_num = game.current_round + 1
    round = GameRound(game_id=game.id, round_number=round_num, dealer_position=3, phase='bidding')
    db.session.add(round)
    game.current_round = round_num
    db.session.commit()
    
    engine.process_bid(players[0].id, 'Abondance')
    engine.process_bid(players[1].id, 'Miserie')
    engine.process_bid(players[2].id, 'Pas')
    engine.process_bid(players[3].id, 'Pas')
    
    db.session.refresh(round)
    assert round.winning_bid == 'Miserie'
    assert round.bidder_id == players[1].id
