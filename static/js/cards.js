/**
 * Card rendering utilities
 */

function createCardElement(suit, rank, clickable = true) {
    const card = document.createElement('div');
    card.className = 'card';
    if (!clickable) {
        card.classList.add('disabled');
    }

    // Translate rank for display
    const rankTranslations = {
        'ace': 'Aas', 'Ace': 'Aas',
        'king': 'Heer', 'King': 'Heer',
        'queen': 'Dame', 'Queen': 'Dame',
        'jack': 'Boer', 'Jack': 'Boer'
    };
    const displayRank = rankTranslations[rank] || rank;

    // Create SVG element
    const img = document.createElement('img');
    img.src = `/api/card/${suit}/${rank}`;
    img.alt = `${suit} ${displayRank}`;
    img.width = 100;
    img.height = 140;

    card.appendChild(img);
    card.dataset.suit = suit;
    card.dataset.rank = rank;
    card.dataset.cardName = `${suit}-${rank}`;

    return card;
}

function createCardBackElement() {
    const card = document.createElement('div');
    card.className = 'card card-back';

    const img = document.createElement('img');
    img.src = '/api/card/back';
    img.alt = 'Card back';
    img.width = 100;
    img.height = 140;

    card.appendChild(img);
    return card;
}

function parseCardName(cardName) {
    const [suit, rank] = cardName.split('-');
    return { suit, rank };
}

function getSuitSymbol(suit) {
    const symbols = {
        'Heart': '♥', 'Harten': '♥',
        'Diamond': '♦', 'Ruiten': '♦',
        'Club': '♣', 'Klaveren': '♣',
        'Spade': '♠', 'Schuppen': '♠'
    };
    return symbols[suit] || '';
}

function getSuitColor(suit) {
    if (['Heart', 'Diamond', 'Harten', 'Ruiten'].includes(suit)) {
        return '#DC2626';
    }
    return '#1F2937';
}
