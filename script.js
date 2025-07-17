document.addEventListener('DOMContentLoaded', async function() {
    // DOM Elements
    const textInput = document.getElementById('text-input');
    const sendTextBtn = document.getElementById('send-text');
    const recordVoiceBtn = document.getElementById('record-voice');
    const toggleListenBtn = document.getElementById('toggle-listen');
    const deleteHistoryBtn = document.getElementById('delete-history');
    const exportTextsBtn = document.getElementById('export-texts');
    const exportVoicesBtn = document.getElementById('export-voices');
    const chatHistory = document.getElementById('chat-history');
    const speakResponseCheckbox = document.getElementById('speak-response');

    // State Variables
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    let isListeningForWakeWord = false;
    let recognition;
    let db;

    // Database Setup
    const DB_NAME = 'AIAssistantDB';
    const DB_VERSION = 1;
    const TEXT_STORE = 'text_messages';
    const VOICE_STORE = 'voice_recordings';

    // Initialize Database
    async function initDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(DB_NAME, DB_VERSION);

            request.onerror = (event) => {
                console.error("Database error:", event.target.error);
                reject("Database error");
            };

            request.onsuccess = (event) => {
                db = event.target.result;
                resolve(db);
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains(TEXT_STORE)) {
                    db.createObjectStore(TEXT_STORE, { keyPath: 'id', autoIncrement: true });
                }
                if (!db.objectStoreNames.contains(VOICE_STORE)) {
                    db.createObjectStore(VOICE_STORE, { keyPath: 'id', autoIncrement: true });
                }
            };
        });
    }

    // Save Text to IndexedDB
    function saveTextToDB(text) {
        return new Promise((resolve, reject) => {
            const transaction = db.transaction([TEXT_STORE], 'readwrite');
            const store = transaction.objectStore(TEXT_STORE);
            
            const request = store.add({
                text: text,
                timestamp: new Date().toISOString()
            });

            request.onsuccess = () => resolve();
            request.onerror = (event) => {
                console.error("Text save error:", event.target.error);
                reject(event.target.error);
            };
        });
    }

    // Save Voice Recording to IndexedDB
    function saveVoiceToDB(blob) {
        return new Promise((resolve, reject) => {
            const transaction = db.transaction([VOICE_STORE], 'readwrite');
            const store = transaction.objectStore(VOICE_STORE);
            
            const reader = new FileReader();
            reader.onload = (event) => {
                const request = store.add({
                    audio: event.target.result,
                    timestamp: new Date().toISOString()
                });

                request.onsuccess = () => resolve();
                request.onerror = (event) => {
                    console.error("Voice save error:", event.target.error);
                    reject(event.target.error);
                };
            };
            reader.readAsArrayBuffer(blob);
        });
    }

    // Load History from IndexedDB
    async function loadHistory() {
        // Load texts
        const texts = await new Promise((resolve) => {
            const transaction = db.transaction([TEXT_STORE], 'readonly');
            const store = transaction.objectStore(TEXT_STORE);
            const request = store.getAll();

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => resolve([]);
        });

        // Load voice recordings
        const voices = await new Promise((resolve) => {
            const transaction = db.transaction([VOICE_STORE], 'readonly');
            const store = transaction.objectStore(VOICE_STORE);
            const request = store.getAll();

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => resolve([]);
        });

        // Display loaded items
        texts.forEach(item => {
            addMessageToHistory(item.text, 'user', 'text', new Date(item.timestamp));
        });

        voices.forEach(item => {
            const blob = new Blob([item.audio], { type: 'audio/wav' });
            const url = URL.createObjectURL(blob);
            addMessageToHistory(url, 'user', 'audio', new Date(item.timestamp));
        });
    }

    // Add Message to Chat History
    function addMessageToHistory(content, sender, type, timestamp = new Date()) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'timestamp';
        timeDiv.textContent = timestamp.toLocaleTimeString();
        messageDiv.appendChild(timeDiv);
        
        if (type === 'text') {
            messageDiv.appendChild(document.createTextNode(content));
            
            // Save to IndexedDB if user message
            if (sender === 'user') {
                saveTextToDB(content).catch(err => {
                    console.error("Failed to save text:", err);
                });
            }
        } 
        else if (type === 'audio') {
            const audio = document.createElement('audio');
            audio.controls = true;
            audio.src = content;
            messageDiv.appendChild(audio);
            
            // Convert URL back to Blob for saving
            fetch(content)
                .then(res => res.blob())
                .then(blob => saveVoiceToDB(blob))
                .catch(err => console.error("Failed to save voice:", err));
        }
        
        chatHistory.appendChild(messageDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    // Initialize Speech Recognition
    function initSpeechRecognition() {
        if ('webkitSpeechRecognition' in window) {
            recognition = new webkitSpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = false;
            
            recognition.onresult = (event) => {
                const transcript = event.results[event.results.length-1][0].transcript;
                if (isListeningForWakeWord && transcript.toLowerCase().includes('hey assistant')) {
                    startRecording();
                }
            };

            recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
            };
        } else {
            toggleListenBtn.disabled = true;
            toggleListenBtn.title = "Speech recognition not supported";
        }
    }

    // Text Handling
    async function sendText() {
        const text = textInput.value.trim();
        if (!text) return;

        addMessageToHistory(text, 'user', 'text');
        fetch('http://127.0.0.1:5000/save_text', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: text }),
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error("Server error:", data.error);
        }
    })
    .catch(error => {
        console.error("Fetch error:", error);
    });

        textInput.value = '';
        
        // Simulate AI response
        setTimeout(() => {
            const response = generateAIResponse(text);
            addMessageToHistory(response, 'assistant', 'text');
            
            if (speakResponseCheckbox.checked) {
                speakText(response);
            }
        }, 1000);
    }

    // Voice Recording
    function startRecording() {
        if (isRecording) return;
        isRecording = true;
        audioChunks = [];
        recordVoiceBtn.classList.add('recording');

        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.ondataavailable = event => {
                    audioChunks.push(event.data);
                };
                mediaRecorder.start();
            })
            .catch(error => {
                console.error('Microphone error:', error);
                isRecording = false;
                recordVoiceBtn.classList.remove('recording');
                alert('Microphone access denied. Please check permissions.');
            });
    }

    async function stopRecording() {
        if (!isRecording) return;
        isRecording = false;
        recordVoiceBtn.classList.remove('recording');

        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            
            await new Promise(resolve => {
                mediaRecorder.onstop = resolve;
            });
            
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const audioUrl = URL.createObjectURL(audioBlob);
            addMessageToHistory(audioUrl, 'user', 'audio');
            
            // Simulate AI response
            setTimeout(() => {
                const response = generateAIResponse("[Voice message]");
                addMessageToHistory(response, 'assistant', 'text');
                
                if (speakResponseCheckbox.checked) {
                    speakText(response);
                }
            }, 1000);
        }
    }

    // Wake Word Detection
    function toggleWakeWordListening() {
        isListeningForWakeWord = !isListeningForWakeWord;
        
        if (isListeningForWakeWord) {
            toggleListenBtn.textContent = 'Listening for "Hey Assistant"...';
            toggleListenBtn.style.backgroundColor = '#27ae60';
            recognition.start();
        } else {
            toggleListenBtn.textContent = 'Enable Wake Word';
            toggleListenBtn.style.backgroundColor = '';
            recognition.stop();
        }
    }

    // Delete History
    async function deleteHistory() {
        if (!confirm('Are you sure you want to delete all history?')) return;

        try {
            // Clear IndexedDB
            await new Promise((resolve) => {
                const transaction = db.transaction([TEXT_STORE, VOICE_STORE], 'readwrite');
                transaction.objectStore(TEXT_STORE).clear();
                transaction.objectStore(VOICE_STORE).clear();
                transaction.oncomplete = resolve;
            });

            // Clear UI
            chatHistory.innerHTML = '';
        } catch (error) {
            console.error('Delete error:', error);
            alert('Failed to delete history');
        }
    }

    // Export Functions
    async function exportTexts() {
        const texts = await new Promise((resolve) => {
            const transaction = db.transaction([TEXT_STORE], 'readonly');
            const store = transaction.objectStore(TEXT_STORE);
            const request = store.getAll();

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => resolve([]);
        });

        if (texts.length === 0) {
            alert('No text messages to export');
            return;
        }

        const blob = new Blob([JSON.stringify(texts, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ai_assistant_texts_${new Date().toISOString()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }

    async function exportVoices() {
        const voices = await new Promise((resolve) => {
            const transaction = db.transaction([VOICE_STORE], 'readonly');
            const store = transaction.objectStore(VOICE_STORE);
            const request = store.getAll();

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => resolve([]);
        });

        if (voices.length === 0) {
            alert('No voice recordings to export');
            return;
        }

        // Export the most recent recording
        const latestVoice = voices[voices.length - 1];
        const blob = new Blob([latestVoice.audio], { type: 'audio/wav' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ai_assistant_voice_${new Date(latestVoice.timestamp).toISOString()}.wav`;
        a.click();
        URL.revokeObjectURL(url);
    }

    // AI Response Generation
    function generateAIResponse(input) {
        const responses = [
            "I understand you said: " + input,
            "Interesting point about: " + input,
            "Let me think about that... " + input,
            "Thanks for sharing: " + input,
            "I've processed your input about: " + input
        ];
        return responses[Math.floor(Math.random() * responses.length)];
    }

    // Text-to-Speech
    function speakText(text) {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            window.speechSynthesis.speak(utterance);
        }
    }

    // Event Listeners
    function setupEventListeners() {
        sendTextBtn.addEventListener('click', sendText);
        recordVoiceBtn.addEventListener('mousedown', startRecording);
        recordVoiceBtn.addEventListener('mouseup', stopRecording);
        recordVoiceBtn.addEventListener('mouseleave', stopRecording);
        toggleListenBtn.addEventListener('click', toggleWakeWordListening);
        deleteHistoryBtn.addEventListener('click', deleteHistory);
        exportTextsBtn.addEventListener('click', exportTexts);
        exportVoicesBtn.addEventListener('click', exportVoices);

        // Touch support
        recordVoiceBtn.addEventListener('touchstart', (e) => {
            e.preventDefault();
            startRecording();
        });
        
        recordVoiceBtn.addEventListener('touchend', (e) => {
            e.preventDefault();
            stopRecording();
        });

        // Keyboard support
        textInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendText();
            }
        });
    }

    // Initialize the app
    async function init() {
        try {
            await initDB();
            await loadHistory();
            initSpeechRecognition();
            setupEventListeners();
        } catch (error) {
            console.error("Initialization error:", error);
            alert("Failed to initialize the app. Please check console for details.");
        }
    }

    init();
});