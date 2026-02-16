from app import app
from models import db, GameRound, Game, Player
from game_engine import GameEngine

with app.app_context():
    game_id = 4
    print(f"Checking Game {game_id}")
    
    engine = GameEngine(game_id)
    round = engine.get_current_round()
    
    if round:
        print(f"Round Phase: {round.phase}")
        print(f"Dealer Pos: {round.dealer_position}")
        print(f"Bids: {round.bids} (Type: {type(round.bids)})")
        
        bids = round.bids or []
        dealer_pos = round.dealer_position
        next_pos = (dealer_pos + 1 + len(bids)) % 4
        print(f"Calculated Next Pos: {next_pos}")
        
        player = Player.query.filter_by(game_id=game_id, position=next_pos).first()
        print(f"Player at Next Pos: {player}")
        if player:
            print(f"Player Name: {player.name}, ID: {player.id}")
            
        bidder = engine.get_current_bidder()
        print(f"Engine.get_current_bidder() returns: {bidder}")
    else:
        print("No active round")
