import pytest
from app import app as flask_app
from models import db, Game, Player, GameRound, Trick, Score
from game_engine import GameEngine

@pytest.fixture
def app():
    # Use in-memory SQLite for testing
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def test_game(app):
    # Create a game and 4 players
    game = Game()
    db.session.add(game)
    db.session.commit()
    
    players = []
    for i in range(4):
        p = Player(
            game_id=game.id,
            name=f"Player {i+1}",
            position=i,
            is_human=(i == 0),
            ai_difficulty='medium'
        )
        db.session.add(p)
        players.append(p)
    db.session.commit()
    
    return game, players
