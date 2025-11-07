const fs = require('fs');
const path = require('path');
const http = require('http');
const express = require('express');
const { Server } = require("socket.io");

const app = express();
const server = http.createServer(app);
const io = new Server(server);

const PORT = process.env.PORT || 3000;
console.log('Server starting...');

// --- Data Loading ---
let countriesData = {};
let distancesData = {};
let directionsData = {}; // NEW: Variable for direction data
let countryNames = [];
try {
    const countriesPath = path.join(__dirname, 'data.json');
    const distancesPath = path.join(__dirname, 'country_distances.json');
    const directionsPath = path.join(__dirname, 'country_directions.json'); // NEW: Path to directions file

    const countriesRaw = fs.readFileSync(countriesPath);
    countriesData = JSON.parse(countriesRaw);

    const distancesRaw = fs.readFileSync(distancesPath);
    distancesData = JSON.parse(distancesRaw);

    // NEW: Load the directions data
    const directionsRaw = fs.readFileSync(directionsPath);
    directionsData = JSON.parse(directionsRaw);

    countryNames = Object.keys(distancesData);
    console.log(`Successfully loaded data for ${countryNames.length} countries.`);
    console.log('Successfully loaded directions data.'); // Confirmation message
} catch (error) {
    console.error('Failed to load data files:', error);
    process.exit(1);
}

// --- Serve Frontend Files ---
const publicPath = path.join(__dirname, '..', 'public');
app.use(express.static(publicPath));

// --- Game State Management ---
let waitingPlayer = null;
const gameRooms = {}; 

function formatValue(value) {
    if (value >= 1e9) return (value / 1e9).toFixed(1) + ' Billion';
    if (value >= 1e6) return (value / 1e6).toFixed(1) + ' Million';
    if (value >= 1e3) return (value / 1e3).toFixed(1) + ' Thousand';
    return value.toString();
}

function startGame(roomName) {
    const room = gameRooms[roomName];
    if (!room) return;
    room.playAgainVotes = [];
    const allCountryNames = Object.keys(countriesData);
    const randomCountryIndex = Math.floor(Math.random() * allCountryNames.length);
    const answerCountryName = allCountryNames[randomCountryIndex];
    room.answerCountry = { name: answerCountryName, exports: countriesData[answerCountryName] };
    room.answer = answerCountryName.toLowerCase();
    room.commoditiesVisible = 3;
    console.log(`New round for room ${roomName}. Answer: ${answerCountryName}`);
    const commodities = room.answerCountry.exports.slice(0, room.commoditiesVisible).map(item => ({ name: item.HS4, value: formatValue(item["Total Trade Value"]) }));
    io.to(roomName).emit('newRound', { commodities });
}

io.on('connection', (socket) => {
    console.log(`Player connected: ${socket.id}`);
    
    socket.on('playerJoining', (data) => {
        const username = data.username ? data.username.trim().slice(0, 15) : 'Anonymous';
        socket.username = username;
        console.log(`Player ${socket.id} set username to: ${username}`);
        if (waitingPlayer) {
            const roomName = `room-${waitingPlayer.id}`;
            waitingPlayer.join(roomName);
            socket.join(roomName);
            gameRooms[roomName] = { players: { [waitingPlayer.id]: waitingPlayer.username, [socket.id]: socket.username }, answer: null, answerCountry: null, commoditiesVisible: 3, playAgainVotes: [] };
            console.log(`Game starting in ${roomName} between ${waitingPlayer.username} and ${socket.username}`);
            io.to(roomName).emit('gameStart', { players: gameRooms[roomName].players, allCountries: countryNames, roomName: roomName });
            startGame(roomName);
            waitingPlayer = null;
        } else {
            waitingPlayer = socket;
            console.log(`Player ${socket.username} (${socket.id}) is waiting.`);
            socket.emit('waiting', { message: "Waiting for an opponent..." });
        }
    });

    socket.on('submitGuess', (data) => {
        const { guess, roomName } = data;
        const room = gameRooms[roomName];
        if (!room) return;

        const answer = room.answer;
        const guesserId = socket.id;
        const guesserUsername = socket.username;
        const sanitizedGuess = guess.toLowerCase();

        if (sanitizedGuess === answer) {
            io.to(roomName).emit('roundOver', { winnerId: guesserId, winnerName: guesserUsername, answer: answer });
            console.log(`Room ${roomName}: Player ${guesserUsername} won!`);
        } else {
            // --- UPDATED: Send raw distance and direction to client ---
            const distance = distancesData[answer] ? distancesData[answer][sanitizedGuess] : null;
            const direction = directionsData[answer] ? directionsData[answer][sanitizedGuess] : null;
            
            const result = { 
                guesserId: guesserId, 
                guesserName: guesserUsername, 
                guess: guess, 
                distance: distance,     // Send the raw number
                direction: direction    // Send the direction string
            };
            io.to(roomName).emit('guessResult', result);
            console.log(`Room ${roomName}: Player ${guesserUsername} guessed ${guess} (Incorrect)`);
            
            if (room.commoditiesVisible < 10) {
                room.commoditiesVisible++;
                const nextCommodityIndex = room.commoditiesVisible - 1;
                const nextCommodityData = room.answerCountry.exports[nextCommodityIndex];
                if (nextCommodityData) {
                    const newCommodity = { name: nextCommodityData.HS4, value: formatValue(nextCommodityData["Total Trade Value"]) };
                    io.to(roomName).emit('addCommodity', { newCommodity });
                }
            }
        }
    });

    socket.on('requestPlayAgain', (data) => {
        const { roomName } = data;
        const room = gameRooms[roomName];
        if (!room) return;
        if (!room.playAgainVotes.includes(socket.id)) {
            room.playAgainVotes.push(socket.id);
        }
        if (room.playAgainVotes.length === 2) {
            startGame(roomName);
        }
    });

    socket.on('disconnect', () => {
        console.log(`Player disconnected: ${socket.id} (${socket.username || ''})`);
        if (waitingPlayer === socket) {
            waitingPlayer = null;
            console.log('The waiting player disconnected.');
        }
        let roomName = null;
        for (const name in gameRooms) {
            if (Object.keys(gameRooms[name].players).includes(socket.id)) {
                roomName = name;
                break;
            }
        }
        if (roomName) {
            const remainingPlayerId = Object.keys(gameRooms[roomName].players).find(id => id !== socket.id);
            if (remainingPlayerId) {
                io.to(remainingPlayerId).emit('opponentLeft', { message: 'Your opponent has disconnected.' });
            }
            delete gameRooms[roomName];
        }
    });
});

server.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});