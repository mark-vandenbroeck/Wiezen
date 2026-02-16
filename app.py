"""
Wiezen Flask Application
Main application file with routes
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for
from models import db, Game, Player, GameRound, Trick, Score
from game_engine import GameEngine
from card_svg import generate_card_svg, generate_card_back_svg
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    """Home page"""
    # Get recent games
    games = Game.query.order_by(Game.created_at.desc()).limit(10).all()
    return render_template('index.html', games=games)


@app.route('/game/new', methods=['POST'])
def new_game():
    """Create a new game"""
    data = request.get_json() or {}
    player_name = data.get('player_name', 'Jij')
    debug_mode = data.get('debug_mode', False)
    ai_difficulties = data.get('ai_difficulties', ['easy', 'medium', 'hard'])
    
    game = GameEngine.create_new_game(
        player_name=player_name,
        debug_mode=debug_mode,
        ai_difficulties=ai_difficulties
    )
    
    # Start first round
    engine = GameEngine(game.id)
    engine.start_new_round()
    
    return jsonify({'game_id': game.id})


@app.route('/game/<int:game_id>')
def game(game_id):
    """Game page"""
    game = Game.query.get_or_404(game_id)
    players = Player.query.filter_by(game_id=game_id).order_by(Player.position).all()
    
    # Convert players to dictionaries for JSON serialization
    players_dict = [p.to_dict() for p in players]
    
    return render_template('game.html', game=game, players=players, players_json=players_dict)


@app.route('/api/game/<int:game_id>/state')
def game_state(game_id):
    """Get current game state"""
    engine = GameEngine(game_id)
    game = engine.game
    game = engine.game
    current_round = engine.get_current_round()
    
    if not current_round:
        return jsonify({'error': 'No active round'})
    
    current_bidder = engine.get_current_bidder()
    current_bidder_id = current_bidder.id if current_bidder else None
    
    # Get players
    players = Player.query.filter_by(game_id=game_id).order_by(Player.position).all()
    
    # Get current trick
    trick = Trick.query.filter_by(
        round_id=current_round.id,
        trick_number=current_round.current_trick
    ).first()
    
    # Get scores
    scores = {}
    for player in players:
        player_scores = Score.query.filter_by(
            game_id=game_id,
            player_id=player.id
        ).all()
        total = sum(s.points for s in player_scores)
        scores[player.id] = total
    
    # Get trick counts for current round
    tricks_won = {}
    for player in players:
        count = Trick.query.filter_by(
            round_id=current_round.id,
            winner_id=player.id
        ).count()
        tricks_won[player.id] = count

    # Build state
    state = {
        'game': game.to_dict(),
        'round': current_round.to_dict(),
        'players': [p.to_dict() for p in players],
        'current_trick': trick.to_dict() if trick else None,
        'last_trick': Trick.query.filter_by(round_id=current_round.id, trick_number=current_round.current_trick - 1).first().to_dict() if current_round.current_trick > 0 else None,
        'scores': scores,
        'tricks_won': tricks_won,
        'current_bidder_id': current_bidder_id
    }
    
    # Sort hands
    if state['round']['hands']:
        for pid, hand in state['round']['hands'].items():
            state['round']['hands'][pid] = GameEngine.sort_cards(hand)
    
    return jsonify(state)


@app.route('/api/game/<int:game_id>/bid', methods=['POST'])
def submit_bid(game_id):
    """Submit a bid"""
    data = request.get_json()
    player_id = data.get('player_id')
    bid = data.get('bid')
    
    engine = GameEngine(game_id)
    result = engine.process_bid(player_id, bid)
    
    return jsonify(result)


@app.route('/api/game/<int:game_id>/play', methods=['POST'])
def play_card(game_id):
    """Play a card"""
    data = request.get_json()
    player_id = data.get('player_id')
    card_name = data.get('card_name')
    
    engine = GameEngine(game_id)
    result = engine.play_card(player_id, card_name)
    
    return jsonify(result)


@app.route('/api/game/<int:game_id>/trump', methods=['POST'])
def select_trump(game_id):
    """Select trump suit (for Solo Slim)"""
    data = request.get_json()
    player_id = data.get('player_id')
    suit = data.get('suit') # e.g. 'Heart'
    
    engine = GameEngine(game_id)
    current_round = engine.get_current_round()
    if not current_round or current_round.bidder_id != player_id:
        return jsonify({'error': 'Not authorized to select trump'})
    
    current_round.trump_suit = suit
    current_round.trump_card = f"{suit}-Ace"
    db.session.commit()
    
    return jsonify({'success': True, 'trump_suit': suit})


@app.route('/api/game/<int:game_id>/ai/bid/<int:player_id>')
def ai_bid(game_id, player_id):
    """Get AI bid"""
    engine = GameEngine(game_id)
    bid = engine.get_ai_bid(player_id)
    
    if bid:
        result = engine.process_bid(player_id, bid)
        return jsonify({'bid': bid, 'result': result})
    
    return jsonify({'error': 'Not an AI player'})


@app.route('/api/game/<int:game_id>/ai/play/<int:player_id>')
def ai_play(game_id, player_id):
    """Get AI card play"""
    engine = GameEngine(game_id)
    card_name = engine.get_ai_card(player_id)
    
    if card_name:
        result = engine.play_card(player_id, card_name)
        return jsonify({'card_name': card_name, 'result': result})
    
    return jsonify({'error': 'Not an AI player'})


@app.route('/api/game/<int:game_id>/valid-cards/<int:player_id>')
def valid_cards(game_id, player_id):
    """Get valid cards for a player"""
    engine = GameEngine(game_id)
    cards = engine.get_valid_cards(player_id)
    
    return jsonify({'valid_cards': cards})


@app.route('/api/card/<suit>/<rank>')
def card_svg(suit, rank):
    """Generate SVG for a card"""
    svg = generate_card_svg(suit, rank)
    return svg, 200, {'Content-Type': 'image/svg+xml'}


@app.route('/api/card/back')
def card_back_svg():
    """Generate SVG for card back"""
    svg = generate_card_back_svg()
    return svg, 200, {'Content-Type': 'image/svg+xml'}


@app.route('/api/game/<int:game_id>/new-round', methods=['POST'])
def new_round(game_id):
    """Start a new round"""
    engine = GameEngine(game_id)
    game_round = engine.start_new_round()
    
    # Sort hands for response
    response = game_round.to_dict()
    if response['hands']:
        for pid, hand in response['hands'].items():
            response['hands'][pid] = GameEngine.sort_cards(hand)
    
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True, port=5005)
