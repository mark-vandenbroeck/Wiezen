import os

class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///wiezen.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Game settings
    DEBUG_MODE = os.environ.get('DEBUG_MODE', 'False').lower() == 'true'
    AI_DIFFICULTY_LEVELS = ['easy', 'medium', 'hard']
    DEFAULT_AI_DIFFICULTY = 'medium'
