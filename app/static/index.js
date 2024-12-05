function typeWriter(chatContainer, element, text, delay = 10, batchSize = 3) {
    let i = 0;

    function type() {
        element.textContent += text.slice(i, i + batchSize); // Add multiple characters at once
        i += batchSize;

        // Scroll the chatContainer to the top

        if (i < text.length) {
            setTimeout(type, delay); // Adjust the delay as needed
        }
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    type();
}



function sendMessage(message) {
    // Sending message to server using fetch API
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        const chatContainer = document.getElementById('chat-container');
        
        // Display the user's message
        const userMessageDiv = document.createElement('div');
        userMessageDiv.classList.add('user-message');
        userMessageDiv.textContent = message;
        chatContainer.appendChild(userMessageDiv);

        // Display the chatbot's response with the typewriter effect
        const botMessageDiv = document.createElement('div');
        botMessageDiv.classList.add('bot-message');
        chatContainer.appendChild(botMessageDiv);
        
        const botResponse = data.response;
        typeWriter(chatContainer,botMessageDiv, botResponse, 50); // You can adjust the typing speed here
    })
    .catch(error => console.error('Error:', error));
}

// Example usage
document.querySelector('#send-message-button').addEventListener('click', () => {
    const message = document.querySelector('#user-message').value;
    sendMessage(message);
});