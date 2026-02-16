from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON

db = SQLAlchemy()

class Game(db.Model):
    """Represents a game session"""
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, completed
    current_round = db.Column(db.Integer, default=0)
    debug_mode = db.Column(db.Boolean, default=False)
    deck_order = db.Column(JSON)  # List of card names
    
    # Relationships
    players = db.relationship('Player', backref='game', lazy=True, cascade='all, delete-orphan')
    rounds = db.relationship('GameRound', backref='game', lazy=True, cascade='all, delete-orphan')
    scores = db.relationship('Score', backref='game', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'status': self.status,
            'current_round': self.current_round,
            'debug_mode': self.debug_mode,
            'deck_order': self.deck_order
        }


class Player(db.Model):
    """Represents a player in a game"""
    __tablename__ = 'players'
    
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    position = db.Column(db.Integer, nullable=False)  # 0=bottom(human), 1=left, 2=top, 3=right
    is_human = db.Column(db.Boolean, default=False)
    ai_difficulty = db.Column(db.String(20))  # easy, medium, hard (null for human)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'position': self.position,
            'is_human': self.is_human,
            'ai_difficulty': self.ai_difficulty
        }


class GameRound(db.Model):
    """Represents a single round of play"""
    __tablename__ = 'game_rounds'
    
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    round_number = db.Column(db.Integer, nullable=False)
    dealer_position = db.Column(db.Integer, nullable=False)
    trump_suit = db.Column(db.String(10))  # Spade, Heart, Diamond, Club
    trump_card = db.Column(db.String(10))  # e.g., "Heart-Ace"
    
    # Bidding results
    winning_bid = db.Column(db.String(20))  # Vraag, Solo, Miserie, etc.
    bidder_id = db.Column(db.Integer, db.ForeignKey('players.id'))
    partner_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=True)
    
    # Round state
    phase = db.Column(db.String(20), default='dealing')  # dealing, bidding, playing, completed
    current_trick = db.Column(db.Integer, default=0)
    
    # Store hands as JSON (for debugging and state restoration)
    hands = db.Column(JSON)  # {player_id: [card_names]}
    
    # Store bids as JSON list: [{player_id, bid}]
    bids = db.Column(JSON, default=list)
    
    # Relationships
    tricks = db.relationship('Trick', backref='round', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'round_number': self.round_number,
            'dealer_position': self.dealer_position,
            'trump_suit': self.trump_suit,
            'trump_card': self.trump_card,
            'winning_bid': self.winning_bid,
            'bidder_id': self.bidder_id,
            'partner_id': self.partner_id,
            'phase': self.phase,
            'current_trick': self.current_trick,
            'hands': self.hands,
            'bids': self.bids or []
        }


class Trick(db.Model):
    """Represents a single trick"""
    __tablename__ = 'tricks'
    
    id = db.Column(db.Integer, primary_key=True)
    round_id = db.Column(db.Integer, db.ForeignKey('game_rounds.id'), nullable=False)
    trick_number = db.Column(db.Integer, nullable=False)
    leader_id = db.Column(db.Integer, db.ForeignKey('players.id'))
    winner_id = db.Column(db.Integer, db.ForeignKey('players.id'))
    
    # Cards played as JSON: [{player_id, card_name, order}]
    cards_played = db.Column(JSON)
    
    def to_dict(self):
        return {
            'id': self.id,
            'trick_number': self.trick_number,
            'leader_id': self.leader_id,
            'winner_id': self.winner_id,
            'cards_played': self.cards_played
        }


class Score(db.Model):
    """Tracks scores for players"""
    __tablename__ = 'scores'
    
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    round_number = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'player_id': self.player_id,
            'round_number': self.round_number,
            'points': self.points
        }
