// chat.js - Main script for the language learning chatbot interface

// DOM Elements
let activeScenario = null;
let activeConversationId = null;
let isProcessing = false;

// Initialize the chat interface when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Event listeners for scenario selection
    const scenarioItems = document.querySelectorAll('.scenario-item');
    scenarioItems.forEach(item => {
        item.addEventListener('click', function() {
            if (isProcessing) return;
            
            // Remove active class from all scenarios
            scenarioItems.forEach(s => s.classList.remove('active'));
            
            // Add active class to selected scenario
            this.classList.add('active');
            
            // Get scenario ID
            const scenarioId = this.getAttribute('data-scenario');
            
            // Start new conversation with this scenario
            startConversation(scenarioId);
        });
    });
    
    // Event listener for chat form submission
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (isProcessing || !activeConversationId) return;
            
            const inputField = document.getElementById('chat-input');
            const message = inputField.value.trim();
            
            if (message) {
                sendMessage(message);
                inputField.value = '';
            }
        });
    }
    
    // Event listener for review button
    const reviewButton = document.getElementById('review-button');
    if (reviewButton) {
        reviewButton.addEventListener('click', function() {
            if (activeConversationId) {
                getReview();
            }
        });
    }
});

/**
 * Start a new conversation with the selected scenario
 * @param {string} scenarioId - The ID of the selected scenario
 */
function startConversation(scenarioId) {
    if (isProcessing) return;
    
    isProcessing = true;
    
    // Show loading state
    const messagesContainer = document.getElementById('chat-messages');
    messagesContainer.innerHTML = `
        <div class="loading-container" style="display: flex; justify-content: center; margin: 2rem 0;">
            <div class="loading"><div></div><div></div><div></div><div></div></div>
        </div>
    `;
    
    // Change chat title to reflect the selected scenario
    const scenarioName = document.querySelector(`[data-scenario="${scenarioId}"]`).getAttribute('data-name');
    document.getElementById('chat-title').textContent = scenarioName;
    
    // Enable chat input
    document.getElementById('chat-input').disabled = false;
    document.getElementById('send-button').disabled = false;
    
    // Store the active scenario
    activeScenario = scenarioId;
    
    // Make API request to start conversation
    fetch('/api/start_conversation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ scenario: scenarioId })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        activeConversationId = data.conversation_id;
        
        // Clear previous messages
        messagesContainer.innerHTML = '';
        
        // Add bot message
        addMessage(data.message);
    })
    .catch(error => {
        console.error('Error starting conversation:', error);
        messagesContainer.innerHTML = `
            <div class="error-message" style="text-align: center; color: var(--error); margin: 2rem 0;">
                Error starting conversation. Please try again.
            </div>
        `;
    })
    .finally(() => {
        isProcessing = false;
    });
}

/**
 * Send a message to the chatbot
 * @param {string} message - The user's message
 */
function sendMessage(message) {
    if (isProcessing || !activeConversationId) return;
    
    isProcessing = true;
    
    // Add user message to the UI immediately
    const userMessage = {
        id: 'temp-' + Date.now(),
        content: message,
        is_user: true,
        timestamp: new Date().toISOString()
    };
    
    addMessage(userMessage);
    
    // Add loading indicator
    const messagesContainer = document.getElementById('chat-messages');
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'message message-bot loading-message';
    loadingIndicator.innerHTML = `
        <div class="loading"><div></div><div></div><div></div><div></div></div>
    `;
    messagesContainer.appendChild(loadingIndicator);
    
    // Scroll to the bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // Make API request to send message
    fetch('/api/send_message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Remove the loading indicator
        document.querySelector('.loading-message')?.remove();
        
        // Update user message if it has errors
        if (data.user_message.errors && data.user_message.errors.length > 0) {
            // Find the temporary user message and update it
            const userMessageElement = document.getElementById('message-' + userMessage.id);
            if (userMessageElement) {
                userMessageElement.id = 'message-' + data.user_message.id;
                
                // Add error highlighting
                const errorsContainer = document.createElement('div');
                errorsContainer.className = 'message-errors';
                
                data.user_message.errors.forEach(error => {
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'message-error';
                    errorDiv.innerHTML = `
                        <div class="error-text">${escapeHtml(error.error_text)}</div>
                        <div class="message-correction">✓ ${escapeHtml(error.correction)}</div>
                    `;
                    errorsContainer.appendChild(errorDiv);
                });
                
                userMessageElement.appendChild(errorsContainer);
            }
        }
        
        // Add bot message
        addMessage(data.bot_message);
    })
    .catch(error => {
        console.error('Error sending message:', error);
        
        // Remove the loading indicator
        document.querySelector('.loading-message')?.remove();
        
        // Add error message
        const errorMessage = {
            id: 'error-' + Date.now(),
            content: 'Sorry, I encountered an error. Please try again.',
            is_user: false,
            timestamp: new Date().toISOString()
        };
        
        addMessage(errorMessage);
    })
    .finally(() => {
        isProcessing = false;
    });
}

/**
 * Add a message to the chat UI
 * @param {object} message - The message object to display
 */
function addMessage(message) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageElement = document.createElement('div');
    
    messageElement.id = 'message-' + message.id;
    messageElement.className = message.is_user ? 'message message-user' : 'message message-bot';
    
    let messageContent = `
        <div class="message-content">${escapeHtml(message.content)}</div>
        <div class="message-time">${formatTimestamp(message.timestamp)}</div>
    `;
    
    // Add translation for bot messages
    if (!message.is_user && message.translated) {
        messageContent += `
            <div class="message-translation bot-translation">${escapeHtml(message.translated)}</div>
        `;
    }
    
    // Add message actions for bot messages
    if (!message.is_user) {
        messageContent += `
            <div class="message-actions">
                <button class="action-button speak-button" data-message-id="${message.id}">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                        <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                        <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
                    </svg>
                    Listen
                </button>
            </div>
        `;
    }
    
    messageElement.innerHTML = messageContent;
    
    // Add errors if message has them
    if (message.errors && message.errors.length > 0) {
        const errorsContainer = document.createElement('div');
        errorsContainer.className = 'message-errors';
        
        message.errors.forEach(error => {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'message-error';
            errorDiv.innerHTML = `
                <div class="error-text">${escapeHtml(error.error_text)}</div>
                <div class="message-correction">✓ ${escapeHtml(error.correction)}</div>
            `;
            errorsContainer.appendChild(errorDiv);
        });
        
        messageElement.appendChild(errorsContainer);
    }
    
    messagesContainer.appendChild(messageElement);
    
    // Add event listener to speak button
    if (!message.is_user) {
        const speakButton = messageElement.querySelector('.speak-button');
        if (speakButton) {
            speakButton.addEventListener('click', function() {
                const messageId = this.getAttribute('data-message-id');
                speakMessage(messageId);
            });
        }
    }
    
    // Scroll to the bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/**
 * Use Text-to-Speech to speak a bot message
 * @param {string} messageId - The ID of the message to speak
 */
function speakMessage(messageId) {
    if (isProcessing) return;
    
    const speakButton = document.querySelector(`.speak-button[data-message-id="${messageId}"]`);
    
    if (speakButton) {
        speakButton.disabled = true;
        speakButton.innerHTML = `
            <div class="loading"><div></div><div></div><div></div><div></div></div>
        `;
    }
    
    // Make API request to get TTS audio
    fetch('/api/get_tts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message_id: messageId })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.audio_data) {
            // Play the audio
            const audio = new Audio(`data:audio/mp3;base64,${data.audio_data}`);
            audio.play();
        }
    })
    .catch(error => {
        console.error('Error getting TTS:', error);
    })
    .finally(() => {
        if (speakButton) {
            speakButton.disabled = false;
            speakButton.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                    <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                    <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
                </svg>
                Listen
            `;
        }
    });
}

/**
 * Get a review of the conversation
 */
function getReview() {
    if (isProcessing || !activeConversationId) return;
    
    isProcessing = true;
    
    // Show review modal loading state
    const reviewContainer = document.getElementById('review-container');
    reviewContainer.style.display = 'block';
    reviewContainer.innerHTML = `
        <div class="review-panel">
            <h2 class="review-title">Generating Your Performance Review...</h2>
            <div style="display: flex; justify-content: center; margin: 2rem 0;">
                <div class="loading"><div></div><div></div><div></div><div></div></div>
            </div>
        </div>
    `;
    
    // Make API request to get review
    fetch('/api/review')
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Render review content
        renderReview(data);
    })
    .catch(error => {
        console.error('Error getting review:', error);
        
        reviewContainer.innerHTML = `
            <div class="review-panel">
                <h2 class="review-title">Error</h2>
                <p style="text-align: center; color: var(--error);">
                    Sorry, we couldn't generate your performance review. Please try again.
                </p>
                <div style="text-align: center; margin-top: 2rem;">
                    <button class="btn btn-primary" onclick="document.getElementById('review-container').style.display = 'none';">Close</button>
                </div>
            </div>
        `;
    })
    .finally(() => {
        isProcessing = false;
    });
}

/**
 * Render the review content
 * @param {object} reviewData - The review data from the API
 */
function renderReview(reviewData) {
    const reviewContainer = document.getElementById('review-container');
    
    // Prepare the error summary content
    let errorSummaryHTML = '';
    
    if (Object.keys(reviewData.error_summary).length === 0) {
        errorSummaryHTML = `
            <div style="text-align: center; margin: 2rem 0;">
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--success)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                    <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
                <p style="color: var(--success); font-size: 1.125rem; font-weight: 500; margin-top: 1rem;">
                    No errors found! Great job!
                </p>
            </div>
        `;
    } else {
        // Build error summary by category
        Object.entries(reviewData.error_summary).forEach(([category, errors]) => {
            let categoryIcon = '';
            
            if (category === 'grammar') {
                categoryIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>`;
            } else if (category === 'vocabulary') {
                categoryIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>`;
            } else if (category === 'syntax') {
                categoryIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6L6 18"></path><path d="M6 6l12 12"></path></svg>`;
            }
            
            let errorListHTML = '';
            errors.forEach(error => {
                errorListHTML += `
                    <div class="error-item">
                        <div class="error-text">${escapeHtml(error.error_text)}</div>
                        <div class="error-correction">${escapeHtml(error.correction)}</div>
                    </div>
                `;
            });
            
            errorSummaryHTML += `
                <div class="error-category">
                    <h3 class="error-category-title">
                        ${categoryIcon}
                        ${capitalizeFirstLetter(category)} Errors (${errors.length})
                    </h3>
                    <div class="error-list">
                        ${errorListHTML}
                    </div>
                </div>
            `;
        });
    }
    
    // Prepare the suggestions content
    let suggestionsHTML = '';
    if (reviewData.suggestions && reviewData.suggestions.length > 0) {
        reviewData.suggestions.forEach(suggestion => {
            suggestionsHTML += `
                <div class="suggestion-item">
                    <div class="suggestion-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                            <polyline points="22 4 12 14.01 9 11.01"></polyline>
                        </svg>
                    </div>
                    <div>${escapeHtml(suggestion)}</div>
                </div>
            `;
        });
    }
    
    // Render the review panel
    reviewContainer.innerHTML = `
        <div class="review-panel">
            <h2 class="review-title">Your Performance Review</h2>
            
            <div class="error-summary">
                ${errorSummaryHTML}
            </div>
            
            <div class="suggestions-container">
                <h3 class="suggestions-title">Improvement Suggestions</h3>
                <div class="suggestion-list">
                    ${suggestionsHTML}
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 2rem; display: flex; justify-content: center; gap: 1rem;">
                <a href="/" class="btn btn-outline" style="display: flex; align-items: center; gap: 0.5rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                        <polyline points="9 22 9 12 15 12 15 22"></polyline>
                    </svg>
                    Return Home
                </a>
                <button class="btn btn-primary" onclick="document.getElementById('review-container').style.display = 'none';">
                    Close Review
                </button>
            </div>
        </div>
    `;
}

/**
 * Format a timestamp into a readable time
 * @param {string} timestamp - ISO timestamp string
 * @returns {string} - Formatted time string
 */
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

/**
 * Capitalize the first letter of a string
 * @param {string} string - The string to capitalize
 * @returns {string} - The capitalized string
 */
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

/**
 * Escape HTML special characters to prevent XSS
 * @param {string} text - The text to escape
 * @returns {string} - The escaped text
 */
function escapeHtml(text) {
    if (!text) return '';
    
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}
