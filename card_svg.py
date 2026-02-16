"""
SVG Card Generator for Wiezen
Creates beautiful custom SVG playing cards
"""

def get_suit_color(suit):
    """Get color for suit"""
    if suit in ['Heart', 'Diamond', 'Harten', 'Ruiten']:
        return '#DC2626'  # Red
    return '#1F2937'  # Dark gray/black


def get_suit_symbol(suit):
    """Get Unicode symbol for suit"""
    symbols = {
        'Heart': '♥',
        'Diamond': '♦',
        'Club': '♣',
        'Spade': '♠',
        'Harten': '♥',
        'Ruiten': '♦',
        'Klaveren': '♣',
        'Schuppen': '♠'
    }
    return symbols.get(suit, '?')


def get_rank_display(rank):
    """Get display value for rank"""
    # Normalize rank to title case to match keys if needed, or add lowercase keys
    rank_map = {
        'Ace': 'A', 'ace': 'A',
        'Two': '2', 'two': '2', '2': '2',
        'Three': '3', 'three': '3', '3': '3',
        'Four': '4', 'four': '4', '4': '4',
        'Five': '5', 'five': '5', '5': '5',
        'Six': '6', 'six': '6', '6': '6',
        'Seven': '7', 'seven': '7', '7': '7',
        'Eight': '8', 'eight': '8', '8': '8',
        'Nine': '9', 'nine': '9', '9': '9',
        'Ten': '10', 'ten': '10', '10': '10',
        'Jack': 'B', 'jack': 'B',
        'Queen': 'D', 'queen': 'D',
        'King': 'H', 'king': 'H'
    }
    return rank_map.get(str(rank), str(rank))


def generate_card_svg(suit, rank, width=100, height=140):
    """
    Generate SVG for a playing card
    
    Args:
        suit: Card suit (Heart, Diamond, Club, Spade)
        rank: Card rank (Ace, Two, ..., King)
        width: Card width in pixels
        height: Card height in pixels
    
    Returns:
        SVG string
    """
    color = get_suit_color(suit)
    symbol = get_suit_symbol(suit)
    rank_text = get_rank_display(rank)
    
    # Calculate positions
    corner_offset = 8
    center_y = height / 2
    center_x = width / 2
    
    svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
    <!-- Card background -->
    <rect x="0" y="0" width="{width}" height="{height}" rx="8" fill="white" stroke="#E5E7EB" stroke-width="2"/>
    
    <!-- Top-left corner -->
    <text x="{corner_offset}" y="{corner_offset + 14}" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="{color}">{rank_text}</text>
    <text x="{corner_offset}" y="{corner_offset + 30}" font-family="Arial, sans-serif" font-size="18" fill="{color}">{symbol}</text>
    
    <!-- Bottom-right corner (rotated) -->
    <g transform="rotate(180, {width/2}, {height/2})">
        <text x="{corner_offset}" y="{corner_offset + 14}" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="{color}">{rank_text}</text>
        <text x="{corner_offset}" y="{corner_offset + 30}" font-family="Arial, sans-serif" font-size="18" fill="{color}">{symbol}</text>
    </g>
    
    <!-- Center symbol -->
    <text x="{center_x}" y="{center_y + 12}" font-family="Arial, sans-serif" font-size="36" fill="{color}" text-anchor="middle">{symbol}</text>
</svg>'''
    
    return svg


def generate_card_back_svg(width=100, height=140):
    """
    Generate SVG for card back
    
    Args:
        width: Card width in pixels
        height: Card height in pixels
    
    Returns:
        SVG string
    """
    svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
    <!-- Card background -->
    <rect x="0" y="0" width="{width}" height="{height}" rx="8" fill="#1E40AF" stroke="#1E3A8A" stroke-width="2"/>
    
    <!-- Pattern -->
    <pattern id="cardPattern" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
        <circle cx="10" cy="10" r="2" fill="#3B82F6" opacity="0.5"/>
    </pattern>
    <rect x="8" y="8" width="{width-16}" height="{height-16}" rx="4" fill="url(#cardPattern)"/>
    
    <!-- Inner border -->
    <rect x="8" y="8" width="{width-16}" height="{height-16}" rx="4" fill="none" stroke="#60A5FA" stroke-width="2"/>
</svg>'''
    
    return svg


def get_card_name(suit, rank):
    """Get card identifier name"""
    return f"{suit}-{rank}"
