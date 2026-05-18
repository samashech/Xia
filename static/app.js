let characters = {};
let selectedCharacterId = null;
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let audioPlayer = new Audio();

const grid = document.getElementById('character-grid');
const chatLog = document.getElementById('chat-log');
const micBtn = document.getElementById('mic-btn');
const statusInd = document.getElementById('status-indicator');

// Fetch Characters on Load
async function fetchCharacters() {
    try {
        const res = await fetch('/api/characters');
        characters = await res.json();
        renderCharacters();
        setupAudioRecording();
    } catch (e) {
        addMessage('system', 'Error connecting to server. Is the backend running?');
    }
}

function renderCharacters() {
    grid.innerHTML = '';
    for (const [id, char] of Object.entries(characters)) {
        const card = document.createElement('div');
        card.className = 'char-card';
        card.innerHTML = `<h3>${char.name}</h3>`;
        card.onclick = () => selectCharacter(id, card);
        grid.appendChild(card);
    }
    // Select first by default
    const firstId = Object.keys(characters)[0];
    if (firstId) {
        selectCharacter(firstId, grid.firstChild);
    }
}

function selectCharacter(id, cardElement) {
    selectedCharacterId = id;
    document.querySelectorAll('.char-card').forEach(c => c.classList.remove('selected'));
    if (cardElement) cardElement.classList.add('selected');
    addMessage('system', `Selected ${characters[id].name}`);
}

async function setupAudioRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = async () => {
            isRecording = false;
            resetMicButton();
            
            const audioBlob = new Blob(audioChunks);
            audioChunks = [];
            
            if (audioBlob.size > 0) {
                await sendAudioToServer(audioBlob);
            }
        };

        // Enable button now that recording is ready
        micBtn.disabled = false;

        // Mouse events for push-to-talk
        micBtn.addEventListener('mousedown', startListening);
        micBtn.addEventListener('mouseup', stopListening);
        micBtn.addEventListener('mouseleave', stopListening);
        
        // Touch events for mobile
        micBtn.addEventListener('touchstart', (e) => { e.preventDefault(); startListening(); });
        micBtn.addEventListener('touchend', (e) => { e.preventDefault(); stopListening(); });

    } catch (err) {
        addMessage('system', `Microphone access denied or not available: ${err.message}`);
    }
}

function startListening() {
    if (!mediaRecorder || isRecording) return;
    
    audioPlayer.pause(); 
    audioChunks = [];
    mediaRecorder.start();
    
    isRecording = true;
    micBtn.classList.add('listening');
    micBtn.querySelector('.mic-text').innerText = 'Release to Send';
    statusInd.innerText = 'Listening...';
}

function stopListening() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
    }
}

function resetMicButton() {
    micBtn.classList.remove('listening');
    micBtn.querySelector('.mic-text').innerText = 'Hold to Talk';
    if (statusInd.innerText === 'Listening...') statusInd.innerText = 'Idle';
}

async function sendAudioToServer(audioBlob) {
    statusInd.innerText = 'Transcribing...';
    micBtn.disabled = true;

    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');
    formData.append('character_id', selectedCharacterId);

    try {
        const response = await fetch('/api/chat_audio', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Server error');
        }

        const data = await response.json();
        
        // Show what the user said
        addMessage('user', data.user_text);
        
        // Show what AI replied
        addMessage('ai', data.text);
        statusInd.innerText = 'Speaking...';
        
        // Play Audio
        const audioSrc = `data:audio/mp3;base64,${data.audio_b64}`;
        audioPlayer.src = audioSrc;
        audioPlayer.onended = () => {
            statusInd.innerText = 'Idle';
        };
        await audioPlayer.play();

    } catch (e) {
        addMessage('system', `Error: ${e.message}`);
        statusInd.innerText = 'Error';
    } finally {
        micBtn.disabled = false;
    }
}

function addMessage(type, text) {
    const div = document.createElement('div');
    div.className = `message ${type}`;
    div.innerText = type === 'system' ? text : `${type === 'user' ? 'You' : characters[selectedCharacterId].name}: ${text}`;
    chatLog.appendChild(div);
    chatLog.scrollTop = chatLog.scrollHeight;
}


fetchCharacters();
