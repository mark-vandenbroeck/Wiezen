import pytest
from app import app, db
from models import Game, Player, GameRound, Trick
from game_engine import GameEngine
from arch.cards.suits import Suit
from arch.cards.ranks import Rank
from arch.cards.cards import Card

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

def setup_game_round(game_id, player_ids):
    round = GameRound(
        game_id=game_id,
        round_number=1,
        phase='playing',
        winning_bid='Vraag',
        bidder_id=player_ids[0],
        current_trick=0,
        dealer_position=0,
        hands={str(pid): ['Heart-Ace', 'Spade-King'] for pid in player_ids},
        trump_suit='Heart'
    )
    db.session.add(round)
    
    # Update game current round to match
    game = Game.query.get(game_id)
    game.current_round = 1
    db.session.add(game)
    
    db.session.commit()
    return round

def test_undo_simple_move(client):
    """Test undoing a single move returns card to hand and resets trick"""
    with app.app_context():
        # Setup
        game = Game()
        db.session.add(game)
        db.session.commit()
        
        players = []
        for i in range(4):
            p = Player(game_id=game.id, name=f"P{i}", position=i, is_human=(i==0))
            db.session.add(p)
            db.session.commit()
            players.append(p)
            
        game_round = setup_game_round(game.id, [p.id for p in players])
        engine = GameEngine(game.id)
        
        # Player 0 plays a card
        trick = Trick(round_id=game_round.id, trick_number=0, leader_id=players[0].id, cards_played=[])
        db.session.add(trick)
        db.session.commit()
        
        result = engine.play_card(players[0].id, 'Heart-Ace')
        
        # Verify played
        assert result.get('status') == 'success'
        trick = Trick.query.filter_by(round_id=game_round.id, trick_number=0).first()
        assert len(trick.cards_played) == 1
        assert 'Heart-Ace' not in game_round.hands[str(players[0].id)]
        
        # Undo
        engine.undo_last_move(players[0].id)
        
        # Verify undone
        trick = Trick.query.filter_by(round_id=game_round.id, trick_number=0).first()
        # Card should be gone from trick
        assert len(trick.cards_played) == 0
        # Card should be back in hand
        # Need to refresh round from DB
        game_round = GameRound.query.get(game_round.id)
        assert 'Heart-Ace' in game_round.hands[str(players[0].id)]

def test_undo_across_ai_moves(client):
    """Test undoing back to human player across AI moves"""
    with app.app_context():
        # Setup
        game = Game()
        db.session.add(game)
        db.session.commit()
        
        players = []
        for i in range(4):
            p = Player(game_id=game.id, name=f"P{i}", position=i, is_human=(i==0))
            db.session.add(p)
            db.session.commit()
            players.append(p)
            
        game_round = setup_game_round(game.id, [p.id for p in players])
        engine = GameEngine(game.id)
        
        # Human (P0) plays, then P1 (AI), P2 (AI) play
        trick = Trick(round_id=game_round.id, trick_number=0, leader_id=players[0].id, cards_played=[])
        db.session.add(trick)
        db.session.commit()
        
        engine.play_card(players[0].id, 'Heart-Ace')
        engine.play_card(players[1].id, 'Heart-Ace') # Validated loosely here
        engine.play_card(players[2].id, 'Heart-Ace')
        
        # Verify 3 cards played
        trick = Trick.query.filter_by(round_id=game_round.id, trick_number=0).first()
        assert len(trick.cards_played) == 3
        
        # Human requests undo
        result = engine.undo_last_move(players[0].id)
        
        assert result.get('success') is True
        
        # Should have undone P2, P1, and P0's moves?
        # Wait, the logic is: undo UNTIL it is player_id's turn.
        # If P0 played, then P1, P2 played.
        # Current turn is P3.
        # Undo P2 -> Turn is P2.
        # Undo P1 -> Turn is P1.
        # Undo P0 -> Turn is P0.
        # Stop.
        # So P0's move is ALSO undone.
        
        trick = Trick.query.filter_by(round_id=game_round.id, trick_number=0).first()
        assert len(trick.cards_played) == 0
        
