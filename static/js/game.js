/**
 * Main game logic and UI management
 */

let gameState = null;
let currentPlayerId = null;
let debugMode = DEBUG_MODE;
let validCards = [];
let isProcessingAI = false;
let isTrickClearing = false;
let lastTrickNum = -1;

// Initialize game
async function initGame() {
    // Find human player
    const humanPlayer = PLAYERS.find(p => p.is_human);
    if (humanPlayer) {
        currentPlayerId = humanPlayer.id;
    }

    // Load initial state
    await updateGameState();

    // Set up event listeners
    setupEventListeners();

    // Start game loop
    gameLoop();
}

function setupEventListeners() {
    // Toggle debug mode
    const debugBtn = document.getElementById('toggle-debug-btn');
    if (debugBtn) {
        debugBtn.addEventListener('click', () => {
            debugMode = !debugMode;
            debugBtn.textContent = debugMode ? 'Debug Uit' : 'Debug Aan';
            renderHands();
        });
    }

    // New round button
    const newRoundBtn = document.getElementById('new-round-btn');
    if (newRoundBtn) {
        newRoundBtn.addEventListener('click', async () => {
            await fetch(`/api/game/${GAME_ID}/new-round`, { method: 'POST' });
            newRoundBtn.style.display = 'none';
            await updateGameState();
            gameLoop();
        });
    }

    // Bidding buttons
    document.querySelectorAll('.btn-bid').forEach(btn => {
        btn.addEventListener('click', () => {
            const bid = btn.getAttribute('data-bid');
            if (bid) {
                submitBid(bid);
            }
        });
    });

    // Trump selection buttons (Solo Slim)
    document.querySelectorAll('.btn-suit').forEach(btn => {
        btn.addEventListener('click', async () => {
            const suit = btn.getAttribute('data-suit');
            if (suit) {
                await selectTrump(suit);
            }
        });
    });
}

/**
 * Handle Solo Slim trump selection
 * @param {string} suit - Suit name
 */
async function selectTrump(suit) {
    try {
        const response = await fetch(`/api/game/${GAME_ID}/trump`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                player_id: currentPlayerId,
                suit: suit
            })
        });
        const result = await response.json();
        if (result.error) {
            alert(result.error);
        } else {
            document.getElementById('trump-modal').classList.remove('active');
            await updateGameState();
        }
    } catch (e) {
        console.error('Error selecting trump:', e);
    }
}

/**
 * Submit a bid to the server
 * @param {string} bid - The bid type (Pas, Vraag, etc.)
 */
async function submitBid(bid) {
    if (!gameState || !currentPlayerId) {
        console.error('Missing state or player ID. GameState:', gameState, 'PID:', currentPlayerId);
        return;
    }

    try {
        const response = await fetch(`/api/game/${GAME_ID}/bid`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                player_id: currentPlayerId,
                bid: bid
            })
        });

        const result = await response.json();
        if (result.error) {
            alert(result.error);
        } else {
            if (result.bid === 'Solo Slim' || result.bid === 'Abondance') {
                // Show trump selection modal if Solo Slim or Abondance won
                document.getElementById('trump-modal').classList.add('active');
                hideBiddingModal();
            } else {
                await updateGameState();
                // Trigger AI check if next player is AI
                checkTurnAndAct();
            }
        }
    } catch (e) {
        console.error('Error submitting bid:', e);
    }
}

let lastGameStateJson = null;

async function updateGameState() {
    const response = await fetch(`/api/game/${GAME_ID}/state`);
    const newState = await response.json();

    if (newState.error) {
        console.error('Error loading game state:', newState.error);
        return;
    }

    // Determine if anything meaningful changed to avoid flickering
    const newStateJson = JSON.stringify(newState);
    const stateChanged = newStateJson !== lastGameStateJson;

    // Check if trick completed (trick number increased)
    if (lastTrickNum !== -1 && newState.round && newState.round.current_trick > lastTrickNum) {
        console.log('Trick completed! Delaying clear...');
        isTrickClearing = true;
        gameState = newState;
        lastGameStateJson = newStateJson;
        lastTrickNum = gameState.round.current_trick;
        renderGameState();

        // Clear after delay and allow next turn
        setTimeout(() => {
            console.log('Clearing trick area.');
            isTrickClearing = false;
            renderTrick();
            checkTurnAndAct();
        }, 3000);
    } else if (stateChanged || isTrickClearing) {
        gameState = newState;
        lastGameStateJson = newStateJson;
        if (gameState.round) {
            lastTrickNum = gameState.round.current_trick;
        }
        renderGameState();
    } else {
        // No change, skip render to avoid flickering
        // console.log('State unchanged, skipping render.');
    }
}

function renderGameState() {
    if (!gameState || !gameState.round) return;

    // Update game info
    document.getElementById('round-number').textContent = gameState.round.round_number;
    document.getElementById('trick-number').textContent = gameState.round.current_trick;

    // Update trump info
    const trumpSuit = gameState.round.trump_suit;
    document.getElementById('trump-suit').textContent = getSuitSymbol(trumpSuit);
    document.getElementById('trump-suit').style.color = getSuitColor(trumpSuit);

    const { suit, rank } = parseCardName(gameState.round.trump_card);
    document.getElementById('trump-card').innerHTML = `
        <img src="/api/card/${suit}/${rank}" width="60" height="84" alt="Trump card">
    `;

    // Update scores
    for (const player of PLAYERS) {
        const scoreEl = document.getElementById(`score-${player.id}`);
        if (scoreEl) {
            scoreEl.textContent = gameState.scores[player.id] || 0;
        }
    }
    // Render announcement for Troel
    const announcement = document.getElementById('troel-announcement');
    const isFirstCardPlayed = gameState.round.current_trick > 0 || (gameState.current_trick && gameState.current_trick.cards_played && gameState.current_trick.cards_played.length > 0);

    if (gameState.round && gameState.round.winning_bid === 'Troel' && !isFirstCardPlayed) {
        const caller = PLAYERS.find(p => p.id === gameState.round.bidder_id);
        const partner = PLAYERS.find(p => p.id === gameState.round.partner_id);
        if (caller && partner && announcement) {
            announcement.innerHTML = `<strong>TROEL!</strong> ${caller.name} heeft 3+ azen en speelt met ${partner.name}.`;
            announcement.style.display = 'block';
        }
    } else if (announcement) {
        announcement.style.display = 'none';
    }

    // Render trick counts per player
    const isPartnership = ['Vraag', 'Troel'].includes(gameState.round.winning_bid);
    const bidderId = gameState.round.bidder_id;
    const partnerId = gameState.round.partner_id;

    for (const player of PLAYERS) {
        const trickEl = document.getElementById(`tricks-${player.id}`);
        if (trickEl) {
            let count = gameState.tricks_won[player.id] || 0;
            let display = true;

            if (isPartnership && gameState.round.phase === 'playing') {
                if (player.id === bidderId) {
                    // Combine partner's tricks
                    const partnerTricks = gameState.tricks_won[partnerId] || 0;
                    count += partnerTricks;
                } else if (player.id === partnerId) {
                    // Hide for partner
                    display = false;
                }
            }

            if (display && gameState.round.phase === 'playing') {
                trickEl.textContent = `Slagen: ${count}`;
                trickEl.style.display = 'inline-block';
            } else {
                trickEl.style.display = 'none';
            }
        }
    }

    // Render Dealer Indicator and Bids
    document.querySelectorAll('.dealer-icon, .bid-bubble, .turn-star').forEach(el => el.remove());

    const dealerPos = gameState.round.dealer_position;
    const dealerPlayer = PLAYERS.find(p => p.position === dealerPos);
    if (dealerPlayer) {
        const dealerInfo = document.querySelector(`.player-area[data-position="${dealerPos}"] .player-info`);
        if (dealerInfo) {
            const icon = document.createElement('span');
            icon.className = 'dealer-icon';
            icon.textContent = '★';
            icon.title = 'Deler';
            dealerInfo.appendChild(icon);
        }
    }

    // Render Turn Indicator (Star)
    PLAYERS.forEach(player => {
        const playerArea = document.querySelector(`.player-area[data-position="${player.position}"]`);
        if (playerArea) {
            let isCurrentTurn = false;
            if (gameState && gameState.round) {
                if (gameState.round.phase === 'bidding' || gameState.round.phase === 'choosing_alleen') {
                    isCurrentTurn = (player.id === gameState.current_bidder_id);
                } else if (gameState.round.phase === 'playing') {
                    const currentTrick = gameState.current_trick;
                    const cardsPlayed = currentTrick ? (currentTrick.cards_played || []).length : 0;
                    if (cardsPlayed < 4) {
                        let nextPlayerId;
                        if (cardsPlayed === 0) {
                            nextPlayerId = currentTrick.leader_id || gameState.round.first_player_id;
                        } else {
                            const lastPlay = currentTrick.cards_played[cardsPlayed - 1];
                            const lastPlayerIndex = PLAYERS.findIndex(p => p.id === lastPlay.player_id);
                            nextPlayerId = PLAYERS[(lastPlayerIndex + 1) % 4].id;
                        }
                        isCurrentTurn = (player.id === nextPlayerId);
                    }
                }
            }

            if (isCurrentTurn) {
                const pInfo = playerArea.querySelector('.player-info');
                if (pInfo) {
                    const star = document.createElement('span');
                    star.className = 'turn-star';
                    star.textContent = '★';
                    star.style.color = '#ffcc00';
                    star.style.marginLeft = '5px';
                    pInfo.appendChild(star);
                }
            }
        }
    });

    // Render Bids
    if (gameState.round.bids && gameState.round.phase !== 'playing') {
        gameState.round.bids.forEach(bid => {
            const player = PLAYERS.find(p => p.id === bid.player_id);
            if (player) {
                const pInfo = document.querySelector(`.player-area[data-position="${player.position}"] .player-info`);
                if (pInfo) {
                    const bubble = document.createElement('div');
                    bubble.className = 'bid-bubble';
                    bubble.textContent = bid.bid;
                    pInfo.appendChild(bubble);
                    pInfo.style.position = 'relative'; // Ensure relative for bubble
                }
            }
        });
    }

    // Special case for badges during playing phase
    if (gameState.round.phase === 'playing' && gameState.round.winning_bid) {
        const pids = [gameState.round.bidder_id];
        if (gameState.round.partner_id) {
            pids.push(gameState.round.partner_id);
        }

        pids.forEach(pid => {
            const player = PLAYERS.find(p => p.id === pid);
            if (player) {
                const pInfo = document.querySelector(`.player-area[data-position="${player.position}"] .player-info`);
                if (pInfo) {
                    const bubble = document.createElement('div');
                    bubble.className = 'bid-bubble';
                    bubble.textContent = gameState.round.winning_bid;
                    pInfo.appendChild(bubble);
                    pInfo.style.position = 'relative';
                }
            }
        });
    }

    // Render hands
    renderHands();

    // Render current trick
    renderTrick();

    // Populate modal trump info
    const mtInfo = document.getElementById('modal-trump-info');
    if (mtInfo && gameState.round) {
        const trumpSuit = gameState.round.trump_suit;
        const { suit, rank } = parseCardName(gameState.round.trump_card);
        const symbol = getSuitSymbol(trumpSuit);
        const color = getSuitColor(trumpSuit);

        mtInfo.innerHTML = `
             <div style="display: flex; flex-direction: column; align-items: center; gap: 5px;">
                 <span style="font-size: 1.2em;">Troef: <span style="color: ${color}; font-weight: bold;">${trumpSuit} ${symbol}</span></span>
                 <img src="/api/card/${suit}/${rank}" width="60" height="84" alt="Trump card" style="border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
             </div>
         `;
    }

    // Check phase and turn for Modal
    if (gameState.round.phase === 'bidding' || gameState.round.phase === 'choosing_alleen') {
        const modal = document.getElementById('bidding-modal');
        // Only show if it matches current player ID
        if (gameState.current_bidder_id === currentPlayerId && currentPlayerId !== null) {
            // Determine valid bids based on history
            const bids = gameState.round.bids || [];
            let maxBidValue = 0;
            let hasVraag = false;

            bids.forEach(b => {
                const val = getBidValue(b.bid);
                if (val > maxBidValue) maxBidValue = val;
                if (b.bid === 'Vraag') hasVraag = true;
            });

            // Update button states
            document.querySelectorAll('.btn-bid').forEach(btn => {
                const bidType = btn.getAttribute('data-bid');
                let enabled = true;

                if (bidType === 'Pas') {
                    enabled = true;
                } else if (bidType === 'Vraag') {
                    enabled = maxBidValue === 0 && !hasVraag;
                } else if (bidType === 'Mee') {
                    enabled = hasVraag && maxBidValue === 1;
                } else if (bidType === 'Abondance') {
                    enabled = maxBidValue < 2;
                } else if (bidType === 'Miserie') {
                    enabled = maxBidValue < 3;
                } else if (bidType === 'Open Miserie') {
                    enabled = maxBidValue < 4;
                } else if (bidType === 'Solo Slim') {
                    enabled = maxBidValue < 5;
                }

                btn.disabled = !enabled;
                btn.style.opacity = enabled ? '1' : '0.5';
                btn.style.cursor = enabled ? 'pointer' : 'not-allowed';
            });

            // Handle Alleen choice
            const biddingOptions = document.getElementById('bidding-options');
            const alleenOptions = document.getElementById('alleen-options');

            if (gameState.round.phase === 'choosing_alleen') {
                biddingOptions.style.display = 'none';
                alleenOptions.style.display = 'flex';
            } else {
                biddingOptions.style.display = 'grid';
                alleenOptions.style.display = 'none';
            }

            if (!modal.classList.contains('active')) {
                setTimeout(() => showBiddingModal(), 300);
            }
        } else {
            hideBiddingModal();
        }
    } else {
        hideBiddingModal();
        if (gameState.round.phase === 'completed') {
            const newRoundBtn = document.getElementById('new-round-btn');
            newRoundBtn.style.display = 'block';

            // Show feedback in trick area if everyone passed
            if (!gameState.round.winning_bid) {
                const trickArea = document.getElementById('trick-area');
                trickArea.innerHTML = `
                    <div style="text-align: center; color: white; background: rgba(0,0,0,0.7); padding: 20px; border-radius: 10px;">
                        <h3>Iedereen gepast!</h3>
                        <p>Klik op 'Nieuwe Ronde' om opnieuw te delen.</p>
                    </div>
                `;
            }
        }
    }

    // Trigger AI turn check
    checkTurnAndAct();
}

function getBidValue(bid) {
    switch (bid) {
        case 'Pas': return 0;
        case 'Vraag': return 1;
        case 'Mee': return 1;
        case 'Abondance': return 2;
        case 'Miserie': return 3;
        case 'Open Miserie': return 4;
        case 'Solo Slim': return 5;
        default: return 0;
    }
}

function renderHands() {
    console.log('Rendering hands...');
    if (!gameState || !gameState.round || !gameState.round.hands) return;

    for (const player of PLAYERS) {
        const handEl = document.getElementById(`hand-${player.id}`);
        if (!handEl) continue;

        handEl.innerHTML = '';

        const cards = gameState.round.hands[player.id] || [];
        const isHuman = player.is_human;

        // Open Miserie Reveal: bidder's hand revealed after trick 1
        let isOpenMiserieReveal = false;
        if (gameState.round.winning_bid === 'Open Miserie' &&
            gameState.round.bidder_id === player.id &&
            gameState.round.current_trick >= 1) {
            isOpenMiserieReveal = true;
        }

        const showCards = isHuman || debugMode || isOpenMiserieReveal;

        console.log(`Player ${player.id} cards:`, cards.length);

        for (const cardName of cards) {
            let cardEl;

            if (showCards) {
                const { suit, rank } = parseCardName(cardName);
                const isValid = validCards.includes(cardName);
                // In bidding phase, validCards is empty, so isValid is false.
                // We want cards to be visible (disabled style ok).
                cardEl = createCardElement(suit, rank, isHuman && isValid);

                if (isHuman && isValid) {
                    cardEl.addEventListener('click', () => playCard(cardName));
                }
            } else {
                cardEl = createCardBackElement();
            }

            handEl.appendChild(cardEl);
        }
    }
}



let lastTrickState = [];

function renderTrick() {
    const trickArea = document.getElementById('trick-area');
    if (!trickArea) return;

    // If we are in the delay period after a trick ends, show the last trick cards
    let trickToShow = gameState.current_trick;
    if (isTrickClearing && gameState.last_trick) {
        trickToShow = gameState.last_trick;
    }

    if (!trickToShow || !trickToShow.cards_played) {
        trickArea.innerHTML = '';
        lastTrickState = [];
        return;
    }

    // Identify the new card to animate
    const currentCards = trickToShow.cards_played;
    const newCards = currentCards.filter(c => !lastTrickState.some(lc => lc.player_id === c.player_id && lc.card_name === c.card_name));

    // Only clear if necessary or if new cards are added
    if (trickArea.innerHTML === '' || newCards.length > 0 || lastTrickState.length > currentCards.length) {
        // We will rebuild the trick area, but we want to animate the new one
        trickArea.innerHTML = '';

        currentCards.forEach((cardPlay, index) => {
            const { suit, rank } = parseCardName(cardPlay.card_name);
            const cardEl = createCardElement(suit, rank, false);
            cardEl.classList.add('card-played');

            // Find player position
            const player = PLAYERS.find(p => p.id === cardPlay.player_id);
            if (player) {
                const posClassMap = ['bottom', 'left', 'top', 'right'];
                const className = `card-played-${posClassMap[player.position]}`;
                cardEl.classList.add(className);
                cardEl.style.zIndex = 10 + index;
            }

            const isNew = newCards.some(nc => nc.player_id === cardPlay.player_id && nc.card_name === cardPlay.card_name);

            if (isNew) {
                // FLIP animation
                // 1. Target (Last) position is already set by classes
                trickArea.appendChild(cardEl);

                // 2. Determine Start (First) position
                const handEl = document.getElementById(`hand-${cardPlay.player_id}`);
                if (handEl) {
                    const handRect = handEl.getBoundingClientRect();
                    const trickRect = trickArea.getBoundingClientRect();

                    // We need to calculate the relative offset
                    const targetRect = cardEl.getBoundingClientRect();

                    const startX = (handRect.left + handRect.width / 2) - (targetRect.left + targetRect.width / 2);
                    const startY = (handRect.top + handRect.height / 2) - (targetRect.top + targetRect.height / 2);

                    // 3. Invert
                    cardEl.classList.add('card-animating');
                    cardEl.style.transform += ` translate(${startX}px, ${startY}px) scale(0.5)`;
                    cardEl.style.opacity = '0';

                    // 4. Play
                    requestAnimationFrame(() => {
                        requestAnimationFrame(() => {
                            cardEl.classList.remove('card-animating');
                            cardEl.style.transform = cardEl.style.transform.replace(/translate\([^)]+\) scale\([^)]+\)/, '');
                            cardEl.style.opacity = '1';
                        });
                    });
                }
            } else {
                trickArea.appendChild(cardEl);
            }
        });
    }

    lastTrickState = [...currentCards];
}
// Bidding
function showBiddingModal() {
    const modal = document.getElementById('bidding-modal');
    modal.classList.add('active');
    document.getElementById('bidding-status').textContent = '';
}

function hideBiddingModal() {
    const modal = document.getElementById('bidding-modal');
    modal.classList.remove('active');
}

// Card playing
async function updateValidCards() {
    if (!currentPlayerId) {
        console.error('updateValidCards: No currentPlayerId');
        return;
    }

    try {
        console.log(`Fetching valid cards for player ${currentPlayerId}...`);
        const response = await fetch(`/api/game/${GAME_ID}/valid-cards/${currentPlayerId}`);
        const data = await response.json();
        validCards = data.valid_cards || [];
        console.log('Valid cards received:', validCards);
    } catch (e) {
        console.error('Error fetching valid cards:', e);
        validCards = [];
    }
}

async function playCard(cardName) {
    console.log(`Attempting to play card: ${cardName}`);
    try {
        const response = await fetch(`/api/game/${GAME_ID}/play`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                player_id: currentPlayerId,
                card_name: cardName
            })
        });

        const result = await response.json();

        if (result.error) {
            console.error('Play card error:', result.error);
            alert(result.error);
            return;
        }

        console.log('Card played successfully');
        await updateGameState();
    } catch (e) {
        console.error('Error playing card:', e);
    }
}
// AI Turn Management
async function checkTurnAndAct() {
    if (isProcessingAI || isTrickClearing || !gameState || !gameState.round) return;

    const phase = gameState.round.phase;

    if (phase === 'bidding' || phase === 'choosing_alleen') {
        const currentBidderId = gameState.current_bidder_id;
        const currentPlayer = PLAYERS.find(p => p.id === currentBidderId);

        if (currentPlayer && !currentPlayer.is_human) {
            isProcessingAI = true;
            await new Promise(resolve => setTimeout(resolve, 1000));

            try {
                const response = await fetch(`/api/game/${GAME_ID}/ai/bid/${currentBidderId}`);
                await response.json();
                await updateGameState();
            } catch (e) {
                console.error('AI Processing Error:', e);
            } finally {
                isProcessingAI = false;
                // Trigger check for next player safely
                setTimeout(checkTurnAndAct, 100);
            }
        } else if (currentPlayer && currentPlayer.is_human) {
            renderHands(); // Ensure modal check runs
        }
    } else if (phase === 'playing') {
        const currentTrick = gameState.current_trick;
        const cardsPlayed = currentTrick ? (currentTrick.cards_played || []).length : 0;
        console.log(`Checking turn. Playing phase. Cards played: ${cardsPlayed}`);

        if (cardsPlayed < 4) {
            // Determine whose turn
            let nextPlayerPosition;
            if (cardsPlayed === 0) {
                if (currentTrick && currentTrick.leader_id) {
                    const leader = PLAYERS.find(p => p.id === currentTrick.leader_id);
                    nextPlayerPosition = leader ? leader.position : 0;
                } else {
                    nextPlayerPosition = (gameState.round.dealer_position + 1) % 4;
                }
            } else {
                const lastPlay = currentTrick.cards_played[cardsPlayed - 1];
                const lastPlayer = PLAYERS.find(p => p.id === lastPlay.player_id);
                nextPlayerPosition = (lastPlayer.position + 1) % 4;
            }

            console.log(`Next player position: ${nextPlayerPosition}`);
            const nextPlayer = PLAYERS.find(p => p.position === nextPlayerPosition);
            console.log(`Next player: ${nextPlayer ? nextPlayer.name : 'Unknown'} (ID: ${nextPlayer ? nextPlayer.id : '?'})`);

            if (nextPlayer && !nextPlayer.is_human) {
                isProcessingAI = true;
                await new Promise(resolve => setTimeout(resolve, 1500));

                try {
                    const response = await fetch(`/api/game/${GAME_ID}/ai/play/${nextPlayer.id}`);
                    const result = await response.json();
                    if (result.result && result.result.trick_complete) {
                        await updateGameState();
                        setTimeout(async () => {
                            await updateGameState();
                        }, 2000); // Wait to show trick result
                    } else {
                        await updateGameState();
                    }
                } finally {
                    isProcessingAI = false;
                    // Trigger check for next player safely
                    setTimeout(checkTurnAndAct, 100);
                }
            } else if (nextPlayer && nextPlayer.is_human) {
                console.log('It is HUMAN turn. Updating valid cards...');
                await updateValidCards();
                renderHands(); // Re-render to show valid cards
            }
        }
    }
}

// Game loop for polling state
function gameLoop() {
    // Poll for game state updates every 2 seconds
    setInterval(async () => {
        if (!isProcessingAI && !isTrickClearing) {
            await updateGameState();
        }
    }, 2000);
}

// Start game when page loads
document.addEventListener('DOMContentLoaded', initGame);
