// No more Socket.IO library! We will define the socket when the user logs in.
let socket;

// --- DOM Element Selection ---
const loginScreen = document.getElementById('login-screen');
const loginForm = document.getElementById('login-form');
const usernameInput = document.getElementById('username-input');
const gameContainer = document.getElementById('game-container');
const statusMessage = document.getElementById('status-message');
const gameContent = document.getElementById('game-content');
const commodityList = document.getElementById('commodity-list');
const selfPlayerArea = document.getElementById('player-self');
const opponentPlayerArea = document.getElementById('player-opponent');
const selfGuessesList = document.getElementById('self-guesses');
const opponentGuessesList = document.getElementById('opponent-guesses');
const guessForm = document.getElementById('guess-form');
const guessInput = document.getElementById('guess-input');
const submitButton = document.getElementById('submit-button');
const autocompleteContainer = document.getElementById('autocomplete-container');
const playAgainContainer = document.getElementById('play-again-container');
const playAgainButton = document.getElementById('play-again-button');

// --- State Management ---
let myPlayerId = null;
let allCountries = [];
let selectedCountry = null;

// --- UI Update Functions (These do not need to change) ---
function updateCommodities(commodities) {
    commodityList.innerHTML = '';
    commodities.forEach(item => {
        const li = document.createElement('li');
        li.className = 'commodity-item';
        li.innerHTML = `<span class="commodity-name">${item.name}</span><span class="commodity-value">${item.value}</span>`;
        commodityList.appendChild(li);
    });
}

function addGuessToHistory(result) {
    const { guesserId, guesserName, guess, distance } = result;
    const guessItem = document.createElement('li');
    guessItem.className = 'guess-item';
    let distanceHtml = (guesserId === myPlayerId) ? `<span class="guess-distance">${distance}</span>` : '';
    let nameHtml = (guesserId === myPlayerId) ? guess : `${guesserName}: ${guess}`;
    guessItem.innerHTML = `<span class="guess-name">${nameHtml}</span> ${distanceHtml}`;

    if (guesserId === myPlayerId) {
        selfGuessesList.appendChild(guessItem);
        selfGuessesList.scrollTop = selfGuessesList.scrollHeight;
    } else {
        opponentGuessesList.appendChild(guessItem);
        opponentGuessesList.scrollTop = opponentGuessesList.scrollHeight;
    }
}

function updateAutocomplete(inputText) {
    autocompleteContainer.innerHTML = '';
    if (!inputText) return;
    const filteredCountries = allCountries.filter(c => c.toLowerCase().startsWith(inputText.toLowerCase()));
    if (filteredCountries.length === 0) return;
    const list = document.createElement('ul');
    list.className = 'autocomplete-list';
    filteredCountries.slice(0, 100).forEach(country => {
        const item = document.createElement('li');
        item.className = 'autocomplete-item';
        item.textContent = country;
        item.addEventListener('mousedown', () => {
            guessInput.value = country;
            selectedCountry = country;
            autocompleteContainer.innerHTML = '';
            submitButton.disabled = false;
        });
        list.appendChild(item);
    });
    autocompleteContainer.appendChild(list);
}

// --- Event Listener for Login Form ---
loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const username = usernameInput.value;
    if (username.trim()) {
        myPlayerId = Math.random().toString(36).substr(2, 9);
        const wsUrl = `wss://exportle-game-server.hastinyre.workers.dev?playerId=${myPlayerId}&username=${encodeURIComponent(username)}`;
        
        // Create the native WebSocket connection
        socket = new WebSocket(wsUrl);

        // --- Attach Event Listeners to the new socket ---
        socket.onopen = () => {
            console.log("WebSocket connection established!");
            statusMessage.textContent = 'Looking for a game...';
        };

        socket.onmessage = (event) => {
            try {
                const { type, payload } = JSON.parse(event.data);
                switch(type) {
                    case 'gameStart':
                        allCountries = payload.allCountries ? payload.allCountries.sort() : [];
                        const myUsername = payload.players[myPlayerId];
                        const opponentId = Object.keys(payload.players).find(id => id !== myPlayerId);
                        const opponentUsername = payload.players[opponentId];
                        selfPlayerArea.querySelector('h2').textContent = `You (${myUsername})`;
                        opponentPlayerArea.querySelector('h2').textContent = `Opponent (${opponentUsername})`;
                        statusMessage.textContent = 'Opponent found!';
                        gameContent.style.display = 'block';
                        break;
                    // ... (other cases are the same)
                     case 'newRound':
                        statusMessage.textContent = "Guess the country!";
                        statusMessage.className = '';
                        updateCommodities(payload.commodities);
                        selfGuessesList.innerHTML = '';
                        opponentGuessesList.innerHTML = '';
                        guessInput.value = '';
                        guessInput.disabled = false;
                        submitButton.disabled = true;
                        selectedCountry = null;
                        playAgainContainer.style.display = 'none';
                        playAgainButton.disabled = false;
                        playAgainButton.textContent = 'Play Again';
                        break;
                    case 'guessResult':
                        addGuessToHistory(payload);
                        if (payload.guesserId === myPlayerId) {
                            guessInput.disabled = false;
                            guessInput.value = '';
                            guessInput.focus();
                        }
                        break;
                    case 'roundOver':
                        const { winnerId, winnerName, answer } = payload;
                        let message = '';
                        if (winnerId === myPlayerId) {
                            message = `You win! The country was ${answer}.`;
                            statusMessage.className = 'winner-announcement win-message';
                        } else {
                            message = `${winnerName} wins! The country was ${answer}.`;
                            statusMessage.className = 'winner-announcement lose-message';
                        }
                        statusMessage.textContent = message;
                        guessInput.disabled = true;
                        submitButton.disabled = true;
                        playAgainContainer.style.display = 'block';
                        break;
                    case 'opponentLeft':
                        statusMessage.textContent = payload.message;
                        statusMessage.className = 'winner-announcement lose-message';
                        guessInput.disabled = true;
                        submitButton.disabled = true;
                        autocompleteContainer.innerHTML = '';
                        playAgainContainer.style.display = 'none';
                        break;
                }
            } catch(err) {
                console.error("Failed to parse message from server:", event.data);
            }
        };

        socket.onclose = () => {
            loginScreen.style.display = 'flex';
            gameContainer.style.display = 'none';
            gameContent.style.display = 'none';
            statusMessage.textContent = 'Connection lost. Please reconnect.';
        };
        
        socket.onerror = (error) => {
            console.error("WebSocket Error:", error);
             statusMessage.textContent = 'Could not connect to the server.';
        };

        loginScreen.style.display = 'none';
        gameContainer.style.display = 'block';
    }
});

// --- Other Event Listeners ---
guessInput.addEventListener('focus', () => updateAutocomplete(guessInput.value));
guessInput.addEventListener('input', () => {
    updateAutocomplete(guessInput.value);
    selectedCountry = null;
    submitButton.disabled = true;
});

document.addEventListener('click', (e) => {
    if (!guessForm.contains(e.target)) {
        autocompleteContainer.innerHTML = '';
    }
});

guessForm.addEventListener('submit', (e) => {
    e.preventDefault();
    if (selectedCountry && socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'submitGuess', payload: { guess: selectedCountry } }));
        guessInput.disabled = true;
        submitButton.disabled = true;
    }
});

playAgainButton.addEventListener('click', () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
        playAgainButton.disabled = true;
        playAgainButton.textContent = 'Waiting for opponent...';
        socket.send(JSON.stringify({ type: 'requestPlayAgain' }));
    }
});