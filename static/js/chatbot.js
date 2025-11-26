function toggleChat() {
    const chatWindow = document.getElementById('chat-window');
    chatWindow.classList.toggle('active');
    
    if (chatWindow.classList.contains('active')) {
        document.getElementById('chat-input').focus();
    }
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Display user message
    addMessage(message, 'user');
    input.value = '';
    
    // Show loading indicator
    const loadingDiv = addMessage('Typing...', 'bot', true);
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        });
        
        if (!response.ok) {
            throw new Error('Failed to get response');
        }
        
        const data = await response.json();
        
        // Remove loading indicator
        loadingDiv.remove();
        
        // Display bot response
        addMessage(data.reply, 'bot');
        
    } catch (error) {
        loadingDiv.remove();
        addMessage('Sorry, I encountered an error. Please try again.', 'bot');
        console.error('Chat error:', error);
    }
}

function addMessage(text, sender, isLoading = false) {
    const chatBody = document.getElementById('chat-body');
    const messageDiv = document.createElement('div');
    messageDiv.className = sender === 'user' ? 'user-message' : 'bot-message';
    
    if (isLoading) {
        messageDiv.classList.add('loading-message');
    }
    
    const p = document.createElement('p');
    p.textContent = text;
    messageDiv.appendChild(p);
    
    chatBody.appendChild(messageDiv);
    
    // Auto scroll to bottom
    chatBody.scrollTop = chatBody.scrollHeight;
    
    return messageDiv;
}
