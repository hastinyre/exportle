const socket = io();

// --- DOM Element Selection ---
const loginScreen = document.getElementById('login-screen');
const loginForm = document.getElementById('login-form');
const usernameInput = document.getElementById('username-input');
const gameContainer = document.getElementById('game-container');
const playerTitles = document.getElementById('player-titles');
const statusMessage = document.getElementById('status-message');
const gameContent = document.getElementById('game-content');
const commodityList = document.getElementById('commodity-list');
const guessHistoryList = document.getElementById('guess-history-list');
const guessForm = document.getElementById('guess-form');
const guessInput = document.getElementById('guess-input');
const submitButton = document.getElementById('submit-button');
const autocompleteContainer = document.getElementById('autocomplete-container');
const playAgainContainer = document.getElementById('play-again-container');
const playAgainButton = document.getElementById('play-again-button');

// --- State Management ---
let myPlayerId = null;
let myRoomName = null;
let allCountries = [];
let selectedCountry = null;

// --- UI Update Functions ---
function updateCommodities(commodities) {
    commodityList.innerHTML = '';
    commodities.forEach(addCommodityToList);
}

function addCommodityToList(commodity) {
    const li = document.createElement('li');
    li.className = 'commodity-item';
    li.innerHTML = `<span class="commodity-name">${commodity.name}</span><span class="commodity-value">${commodity.value}</span>`;
    commodityList.appendChild(li);
    li.style.backgroundColor = '#e0efff';
    setTimeout(() => { li.style.backgroundColor = ''; }, 750);
}

// --- UPDATED: Guess History Formatting ---
function addGuessToHistory(result) {
    const { guesserId, guesserName, guess, distance } = result;
    const guessItem = document.createElement('li');
    guessItem.className = 'guess-item';

    if (guesserId === myPlayerId) {
        guessItem.classList.add('my-guess');
        guessItem.innerHTML = `Target is ${distance} from <span class="guess-country">${guess}</span>`;
    } else {
        guessItem.classList.add('opponent-guess');
        guessItem.textContent = `${guesserName} guessed ${guess}`;
    }
    guessHistoryList.appendChild(guessItem);
    guessHistoryList.scrollTop = guessHistoryList.scrollHeight;
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

// --- Socket Event Listeners ---
socket.on('connect', () => { myPlayerId = socket.id; });
socket.on('waiting', (data) => { statusMessage.textContent = data.message; });

socket.on('gameStart', (data) => {
    gameContent.style.display = 'block';
    allCountries = data.allCountries.sort();
    myRoomName = data.roomName;
    const myUsername = data.players[myPlayerId];
    const opponentId = Object.keys(data.players).find(id => id !== myPlayerId);
    const opponentUsername = data.players[opponentId];
    playerTitles.textContent = `${myUsername} vs ${opponentUsername}`;
});

socket.on('newRound', (data) => {
    statusMessage.textContent = "Guess the country!";
    statusMessage.className = '';
    updateCommodities(data.commodities);
    guessHistoryList.innerHTML = '';
    guessInput.value = '';
    guessInput.disabled = false;
    submitButton.disabled = true;
    selectedCountry = null;
    playAgainContainer.style.display = 'none';
    playAgainButton.disabled = false;
    playAgainButton.textContent = 'Play Again';
});

socket.on('addCommodity', (data) => {
    addCommodityToList(data.newCommodity);
});

socket.on('guessResult', (result) => {
    addGuessToHistory(result);
    if (result.guesserId === myPlayerId) {
        guessInput.disabled = false;
        guessInput.value = '';
        guessInput.focus();
        selectedCountry = null;
        submitButton.disabled = true;
    }
});

socket.on('roundOver', (data) => {
    const { winnerId, winnerName, answer } = data;
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
});

socket.on('opponentLeft', (data) => {
    statusMessage.textContent = data.message;
    statusMessage.className = 'winner-announcement lose-message';
    guessInput.disabled = true;
    submitButton.disabled = true;
    autocompleteContainer.innerHTML = '';
    playAgainContainer.style.display = 'none';
});

socket.on('disconnect', () => {
    loginScreen.style.display = 'flex';
    gameContainer.style.display = 'none';
});

// --- Event Listeners for Forms ---
loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const username = usernameInput.value;
    if (username.trim()) {
        socket.emit('playerJoining', { username });
        loginScreen.style.display = 'none';
        gameContainer.style.display = 'block';
        statusMessage.textContent = 'Connected! Waiting for a game...';
    }
});

guessInput.addEventListener('focus', () => updateAutocomplete(guessInput.value));
guessInput.addEventListener('input', () => {
    updateAutocomplete(guessInput.value);
    selectedCountry = null;
    submitButton.disabled = true;
});

document.addEventListener('click', (e) => {
    if (!guessForm.contains(e.target)) autocompleteContainer.innerHTML = '';
});

guessForm.addEventListener('submit', (e) => {
    e.preventDefault();
    if (selectedCountry && myRoomName) {
        socket.emit('submitGuess', { guess: selectedCountry, roomName: myRoomName });
        guessInput.disabled = true;
        submitButton.disabled = true;
    }
});

playAgainButton.addEventListener('click', () => {
    playAgainButton.disabled = true;
    playAgainButton.textContent = 'Waiting for opponent...';
    socket.emit('requestPlayAgain', { roomName: myRoomName });
});