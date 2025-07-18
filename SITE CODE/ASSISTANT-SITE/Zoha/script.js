document.addEventListener('DOMContentLoaded', function() {
  // Initialize chat
  const chatMessages = JSON.parse(localStorage.getItem('smartHomeChat')) || [
    { role: 'assistant', content: "Hello! I'm your AI home assistant. How can I help you today?" }
  ];
  
  const chatContainer = document.getElementById('chat-messages');
  const messageInput = document.getElementById('message-input');
  const sendButton = document.getElementById('send-message');
  const voiceButton = document.getElementById('voice-toggle');
  
  let isListening = false;
  let socket;
  let reconnectAttempts = 0;
  const maxReconnectAttempts = 5;

  // Initialize WebSocket connection
  function connectWebSocket() {
    socket = new WebSocket('ws://localhost:8765');

    socket.onopen = function(e) {
      console.log('WebSocket connection established');
      reconnectAttempts = 0; // Reset counter on successful connection
    };

    socket.onerror = function(error) {
      console.error('WebSocket Error:', error);
      handleDisconnection();
    };

    socket.onclose = function(e) {
      console.log('WebSocket closed');
      handleDisconnection();
    };

    socket.onmessage = function(event) {
      const response = event.data;
      updateChatWithResponse(response);
    };
  }

  // Handle disconnection with exponential backoff
  function handleDisconnection() {
    if (reconnectAttempts < maxReconnectAttempts) {
      const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
      reconnectAttempts++;
      console.log(`Attempting reconnect #${reconnectAttempts} in ${delay}ms`);
      setTimeout(connectWebSocket, delay);
    } else {
      console.error('Max reconnection attempts reached');
      updateChatWithResponse("Connection lost. Please refresh the page.");
    }
  }

  // Update chat with server response
  function updateChatWithResponse(response) {
    if (chatMessages.length > 0 && 
        chatMessages[chatMessages.length-1].content === "Processing your request...") {
      chatMessages.pop();
    }
    
    chatMessages.push({
      role: 'assistant',
      content: response
    });
    
    saveMessages();
    renderChatMessages();
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }

  // Send message handler
  function handleSendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    // Add user message to chat
    chatMessages.push({ role: 'user', content: message });
    
    // Add processing message
    chatMessages.push({
      role: 'assistant',
      content: "Processing your request..."
    });
    
    // Update UI
    messageInput.value = '';
    renderChatMessages();
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // Try to send via WebSocket
    try {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(message);
      } else {
        throw new Error('WebSocket not connected');
      }
    } catch (error) {
      console.error('Send error:', error);
      updateChatWithResponse("Failed to send message. Reconnecting...");
      connectWebSocket(); // Attempt reconnect
    }
  }

  // Voice toggle handler
  function handleVoiceToggle() {
    isListening = !isListening;
    const micIcon = voiceButton.querySelector('i');
    
    if (isListening) {
      voiceButton.classList.add('btn-primary');
      voiceButton.classList.remove('btn-outline');
      micIcon.classList.remove('lucide-mic');
      micIcon.classList.add('lucide-mic-off');
      console.log('Voice recognition started');
      // Add your voice recognition logic here
    } else {
      voiceButton.classList.remove('btn-primary');
      voiceButton.classList.add('btn-outline');
      micIcon.classList.add('lucide-mic');
      micIcon.classList.remove('lucide-mic-off');
      console.log('Voice recognition stopped');
    }
  }

  // Render chat messages
  function renderChatMessages() {
    chatContainer.innerHTML = '';
    chatMessages.forEach(msg => {
      const messageDiv = document.createElement('div');
      messageDiv.className = `message message-${msg.role}`;
      
      const contentDiv = document.createElement('div');
      contentDiv.className = 'message-content';
      contentDiv.textContent = msg.content;
      
      messageDiv.appendChild(contentDiv);
      chatContainer.appendChild(messageDiv);
    });
  }

  // Save messages to localStorage
  function saveMessages() {
    localStorage.setItem('smartHomeChat', JSON.stringify(chatMessages));
  }

  // Initialize
  connectWebSocket();
  renderChatMessages();
  voiceButton.classList.add('btn-outline');

  // Event listeners
  sendButton.addEventListener('click', handleSendMessage);
  voiceButton.addEventListener('click', handleVoiceToggle);
  
  messageInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  });
});