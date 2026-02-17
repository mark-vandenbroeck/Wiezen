/**
 * Stats Dashboard Logic
 */
const stats_loaded = true;

document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();

        console.log('Stats loaded:', stats);

        renderSummary(stats);
        renderPlayerChart(stats.players);
        renderContractChart(stats.contracts);
        renderLeaderboard(stats.players);

    } catch (e) {
        console.error('Error loading stats:', e);
    }
});

function renderSummary(stats) {
    document.getElementById('total-games').textContent = stats.completed_games;

    // Find "Jij" or human player in stats
    const human = stats.players.find(p => p.name === 'Jij') || { wins: 0 };
    document.getElementById('user-wins').textContent = human.wins;

    const winRate = stats.completed_games > 0 ? (human.wins / stats.completed_games * 100).toFixed(0) : 0;
    document.getElementById('win-rate').textContent = `${winRate}%`;
}

function renderPlayerChart(players) {
    const ctx = document.getElementById('playerChart').getContext('2d');

    // Limit to top 5 for clarity
    const topPlayers = players.slice(0, 5);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topPlayers.map(p => p.name),
            datasets: [{
                label: 'Aantal Wins',
                data: topPlayers.map(p => p.wins),
                backgroundColor: [
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(139, 92, 246, 0.8)',
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(239, 68, 68, 0.8)'
                ],
                borderRadius: 8,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: '#94A3B8', stepSize: 1 },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                },
                x: {
                    ticks: { color: '#94A3B8' },
                    grid: { display: false }
                }
            }
        }
    });
}

function renderContractChart(contracts) {
    const ctx = document.getElementById('contractChart').getContext('2d');

    const labels = Object.keys(contracts);
    const data = Object.values(contracts);

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#3B82F6', '#8B5CF6', '#10B981', '#F59E0B', '#EF4444',
                    '#6366F1', '#EC4899', '#14B8A6'
                ],
                borderWidth: 0,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#94A3B8',
                        padding: 20,
                        usePointStyle: true,
                        font: { size: 12 }
                    }
                }
            },
            cutout: '70%'
        }
    });
}

function renderLeaderboard(players) {
    const body = document.getElementById('leaderboard-body');
    body.innerHTML = '';

    players.forEach(p => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="player-name-cell">
                <span class="rank-indicator ${p.wins > 0 ? 'top-tier' : ''}">${p.name}</span>
            </td>
            <td>${p.wins}</td>
            <td>${p.points}</td>
            <td>${p.avg_points}</td>
        `;
        body.appendChild(row);
    });
}
