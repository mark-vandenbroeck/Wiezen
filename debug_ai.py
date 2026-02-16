from app import app
from models import db, GameRound, Game, Player
from game_engine import GameEngine
import traceback

with app.app_context():
    game_id = 4
    player_id = 15 # AI Boven
    
    print(f"Debugging AI Boven (ID {player_id}) for Game {game_id}")
    
    try:
        engine = GameEngine(game_id)
        bid = engine.get_ai_bid(player_id)
        print(f"AI Bid: {bid}")
    except Exception:
        traceback.print_exc()
