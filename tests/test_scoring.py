import pytest
from models import db, GameRound, Trick, Score
from game_engine import GameEngine

def setup_round_with_tricks(game, players, winning_bid, bidder_idx, partner_idx, trick_counts):
    """
    Helper to set up a round in 'playing' phase and simulate completed tricks.
    trick_counts: {player_index: count}
    """
    game_round = GameRound(
        game_id=game.id,
        round_number=game.current_round + 1,
        dealer_position=0,
        trump_suit="Heart",
        trump_card="Heart-Ace",
        phase='playing',
        winning_bid=winning_bid,
        bidder_id=players[bidder_idx].id,
        partner_id=players[partner_idx].id if partner_idx is not None else None,
        hands={} # Not needed for score calculation
    )
    db.session.add(game_round)
    db.session.flush()
    
    # Create tricks to match trick_counts
    trick_num = 0
    for p_idx, count in trick_counts.items():
        for _ in range(count):
            trick = Trick(
                round_id=game_round.id,
                trick_number=trick_num,
                leader_id=players[0].id, # Doesn't matter for counting
                winner_id=players[p_idx].id,
                cards_played=[{"player_id": players[0].id, "card_name": "Heart-Two"}] # Minimal
            )
            db.session.add(trick)
            trick_num += 1
            
    db.session.commit()
    return game_round

def test_vraag_mee_win(app, test_game):
    game, players = test_game
    engine = GameEngine(game.id)
    
    # Vraag/Mee: P1 bidder, P2 partner. They win 9 tricks (target 8).
    # Base 2 points + 1 overtrick = 3 points per defender.
    # Total transfer from 2 defenders = 6 points.
    # P1 and P2 get 3 each. P3 and P4 lose 3 each.
    game_round = setup_round_with_tricks(game, players, 'Vraag', 0, 1, {0: 5, 1: 4, 2: 2, 3: 2})
    
    engine._calculate_scores(game_round)
    
    scores = Score.query.filter_by(round_number=game_round.round_number).all()
    score_map = {s.player_id: s.points for s in scores}
    
    assert score_map[players[0].id] == 3
    assert score_map[players[1].id] == 3
    assert score_map[players[2].id] == -3
    assert score_map[players[3].id] == -3

def test_vraag_mee_loss(app, test_game):
    game, players = test_game
    engine = GameEngine(game.id)
    
    # Vraag/Mee: P1 bidder, P2 partner. They win 6 tricks (target 8).
    # Fallen by 2 tricks. Base 2 points + 2 penalty = 4 points.
    # points_per_defender = -(2 + (8-6)) = -4
    # Total transfer = -4 * 2 = -8
    # Attacker split: -4 each. Defenders get 4 each.
    game_round = setup_round_with_tricks(game, players, 'Vraag', 0, 1, {0: 3, 1: 3, 2: 4, 3: 3})
    
    engine._calculate_scores(game_round)
    
    scores = Score.query.filter_by(round_number=game_round.round_number).all()
    score_map = {s.player_id: s.points for s in scores}
    
    assert score_map[players[0].id] == -4
    assert score_map[players[1].id] == -4
    assert score_map[players[2].id] == 4
    assert score_map[players[3].id] == 4

def test_alleen_win(app, test_game):
    game, players = test_game
    engine = GameEngine(game.id)
    
    # Alleen: P1 bidder, wins 6 tricks (target 5).
    # Base 2 points + 1 overtrick = 3 points per defender.
    # Total transfer from 3 defenders = 9 points.
    # P1 gets 9. P2, P3, P4 lose 3 each.
    game_round = setup_round_with_tricks(game, players, 'Alleen', 0, None, {0: 6, 1: 2, 2: 3, 3: 2})
    
    engine._calculate_scores(game_round)
    
    scores = Score.query.filter_by(round_number=game_round.round_number).all()
    score_map = {s.player_id: s.points for s in scores}
    
    assert score_map[players[0].id] == 9
    assert score_map[players[1].id] == -3
    assert score_map[players[2].id] == -3
    assert score_map[players[3].id] == -3

def test_abondance_win(app, test_game):
    game, players = test_game
    engine = GameEngine(game.id)
    
    # Abondance: P1 bidder, wins 9 tricks (target 9).
    # Fixed 8 points per defender.
    # Total transfer = 8 * 3 = 24.
    game_round = setup_round_with_tricks(game, players, 'Abondance', 0, None, {0: 9, 1: 2, 2: 1, 3: 1})
    
    engine._calculate_scores(game_round)
    
    scores = Score.query.filter_by(round_number=game_round.round_number).all()
    score_map = {s.player_id: s.points for s in scores}
    
    assert score_map[players[0].id] == 24
    assert score_map[players[1].id] == -8
    assert score_map[players[2].id] == -8
    assert score_map[players[3].id] == -8

def test_miserie_win(app, test_game):
    game, players = test_game
    engine = GameEngine(game.id)
    
    # Miserie: P1 bidder, wins 0 tricks.
    # Fixed 12 points per defender.
    # Total transfer = 12 * 3 = 36.
    game_round = setup_round_with_tricks(game, players, 'Miserie', 0, None, {0: 0, 1: 5, 2: 4, 3: 4})
    
    engine._calculate_scores(game_round)
    
    scores = Score.query.filter_by(round_number=game_round.round_number).all()
    score_map = {s.player_id: s.points for s in scores}
    
    assert score_map[players[0].id] == 36
    assert score_map[players[1].id] == -12

def test_solo_slim_win(app, test_game):
    game, players = test_game
    engine = GameEngine(game.id)
    
    # Solo Slim: P1 bidder, wins 13 tricks.
    # Fixed 24 points per defender.
    # Total transfer = 24 * 3 = 72.
    game_round = setup_round_with_tricks(game, players, 'Solo Slim', 0, None, {0: 13, 1: 0, 2: 0, 3: 0})
    
    engine._calculate_scores(game_round)
    
    scores = Score.query.filter_by(round_number=game_round.round_number).all()
    score_map = {s.player_id: s.points for s in scores}
    
    assert score_map[players[0].id] == 72
    assert score_map[players[1].id] == -24

def test_troel_win(app, test_game):
    game, players = test_game
    engine = GameEngine(game.id)
    
    # Troel: P1 bidder (caller), P2 partner (4th Ace).
    # Scores same as Vraag/Mee.
    game_round = setup_round_with_tricks(game, players, 'Troel', 0, 1, {0: 5, 1: 3, 2: 3, 3: 2})
    
    engine._calculate_scores(game_round)
    
    scores = Score.query.filter_by(round_number=game_round.round_number).all()
    score_map = {s.player_id: s.points for s in scores}
    
    # Attacker wins 8 tricks. Base 2 points.
    # Total transfer 4 points. P1, P2 get 2. P3, P4 lose 2.
    assert score_map[players[0].id] == 2
    assert score_map[players[1].id] == 2
    assert score_map[players[2].id] == -2
    assert score_map[players[3].id] == -2

def test_all_passed(app, test_game):
    game, players = test_game
    engine = GameEngine(game.id)
    
    # All passed: winning_bid is 'Pas'.
    # _calculate_scores should return early and not crash.
    game_round = GameRound(
        game_id=game.id,
        round_number=game.current_round + 1,
        dealer_position=0,
        phase='completed',
        winning_bid='Pas'
    )
    db.session.add(game_round)
    db.session.commit()
    
    engine._calculate_scores(game_round)
    
    scores = Score.query.filter_by(round_number=game_round.round_number).all()
    assert len(scores) == 0
