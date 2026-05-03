// Chat Widget JavaScript
class ChatWidget {
    constructor() {
        this.isMinimized = false;
        this.isLoading = false;
        this.sessionId = null;
        this.init();
    }

    init() {
        this.createWidget();
        this.createFab();
        this.bindEvents();
        this.loadChatHistory();
        this.toggleMinimize();
    }

    createWidget() {
        const widgetHTML = `
            <div class="chat-widget" id="chatWidget">
                <div class="chat-header" id="chatHeader">
                    <h3 style='color:white;'>🏠 PropKart Assistant</h3>
                    <div class="chat-controls">
                        <button id="clearBtn" title="Clear chat">🧹</button>
                        <button id="minimizeBtn" title="Minimize">−</button>
                        <button id="closeBtn" title="Close">×</button>
                    </div>
                </div>
                <div class="chat-messages" id="chatMessages">
                    <div class="chat-message assistant">
                        <div class="message-bubble assistant">
                            👋 Welcome to PropKart! I'm your property assistant. I can help you find your dream property based on your requirements. 
                            Try asking me about properties in specific areas, price ranges, or property types!
                        </div>
                        <div class="message-time assistant">Just now</div>
                    </div>
                </div>
                <div class="chat-input-container">
                    <div class="chat-input-wrapper">
                        <textarea 
                            class="chat-input" 
                            id="chatInput" 
                            placeholder="Ask me about properties..."
                            rows="1"
                        ></textarea>
                        <button class="send-button" id="sendBtn">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', widgetHTML);
        
        // Get references to elements
        this.widget = document.getElementById('chatWidget');
        this.header = document.getElementById('chatHeader');
        this.messages = document.getElementById('chatMessages');
        this.input = document.getElementById('chatInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.minimizeBtn = document.getElementById('minimizeBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.closeBtn = document.getElementById('closeBtn');
    }

    createFab() {
        const fabHTML = `
            <button id="chatFab" class="chat-fab" aria-label="Open chat">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                    <path d="M20 2H4a2 2 0 0 0-2 2v18l4-4h14a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2z"/>
                </svg>
            </button>
        `;
        document.body.insertAdjacentHTML('beforeend', fabHTML);
        this.fab = document.getElementById('chatFab');
        if (this.fab) {
            // Hide FAB initially while widget is open
            this.fab.style.display = 'none';
        }
    }

    bindEvents() {
        // Send message on button click
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        
        // Send message on Enter key (but allow Shift+Enter for new lines)
        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize textarea
        this.input.addEventListener('input', () => {
            this.input.style.height = 'auto';
            this.input.style.height = Math.min(this.input.scrollHeight, 100) + 'px';
        });

        // Minimize/maximize
        this.minimizeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleMinimize();
        });

        // Clear chat
        this.clearBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            await this.clearChat();
        });

        // Close widget
        this.closeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.hideWidget();
        });

        // FAB toggles chat visibility/minimize
        if (this.fab) {
            this.fab.addEventListener('click', () => {
                if (this.widget.classList.contains('hidden')) {
                    this.showWidget();
                    this.isMinimized = false;
                    this.widget.classList.remove('minimized');
                    this.minimizeBtn.textContent = '−';
                } else if (this.isMinimized) {
                    this.toggleMinimize();
                } else {
                    this.toggleMinimize();
                }
            });
        }

        // Toggle minimize on header click
        this.header.addEventListener('click', () => {
            if (this.isMinimized) {
                this.toggleMinimize();
            }
        });
    }

    async clearChat() {
        if (this.isLoading) return;
        this.isLoading = true;
        this.clearBtn.disabled = true;
        try {
            const response = await fetch('/api/chat/clear/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            const data = await response.json();
            if (data.success) {
                // Reset UI: wipe messages and re-show welcome
                this.messages.innerHTML = `
                    <div class="chat-message assistant">
                        <div class="message-bubble assistant">
                            👋 Chat cleared. I can help you find properties. Ask me anything!
                        </div>
                        <div class="message-time assistant">Just now</div>
                    </div>
                `;
                this.sessionId = data.session_id || null;
                this.input.value = '';
                this.input.style.height = 'auto';
                this.scrollToBottom();
            } else {
                this.addMessage('assistant', `Could not clear chat: ${data.error || 'Unknown error'}`);
            }
        } catch (err) {
            console.error('Clear chat error:', err);
            this.addMessage('assistant', 'Sorry, failed to clear chat. Please try again.');
        } finally {
            this.isLoading = false;
            this.clearBtn.disabled = false;
        }
    }

    async sendMessage() {
        const message = this.input.value.trim();
        if (!message || this.isLoading) return;

        // Add user message to chat
        this.addMessage('user', message);
        this.input.value = '';
        this.input.style.height = 'auto';

        // Show typing indicator
        this.showTypingIndicator();

        try {
            const response = await fetch('/api/chat/ask/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            
            if (data.success) {
                this.hideTypingIndicator();
                this.addMessage('assistant', data.response, data.referenced_properties);
                this.sessionId = data.session_id;
            } else {
                this.hideTypingIndicator();
                this.addMessage('assistant', `Sorry, I encountered an error: ${data.error}`);
            }
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('assistant', 'Sorry, I\'m having trouble connecting. Please try again later.');
            console.error('Chat error:', error);
        }
    }

    addMessage(type, content, referencedProperties = []) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${type}`;

        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        let propertyLinksHTML = '';
        if (referencedProperties && referencedProperties.length > 0) {
            propertyLinksHTML = `
                <div class="property-links">
                    <h4>Related Properties</h4>
                    ${referencedProperties.map(propId => 
                        `<a href="/property/${propId}/" class="property-link" target="_blank">
                            View Property #${propId}
                        </a>`
                    ).join('')}
                </div>
            `;
        }

        messageDiv.innerHTML = `
            <div class="message-bubble ${type}">
                ${content.replace(/\n/g, '<br>')}
                ${propertyLinksHTML}
            </div>
            <div class="message-time ${type}">${time}</div>
        `;

        this.messages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showTypingIndicator() {
        this.isLoading = true;
        this.sendBtn.disabled = true;

        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message assistant';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <div class="message-bubble assistant">
                <div class="typing-indicator">
                    Assistant is typing
                    <div class="typing-dots">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                </div>
            </div>
        `;

        this.messages.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.isLoading = false;
        this.sendBtn.disabled = false;
        
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    scrollToBottom() {
        this.messages.scrollTop = this.messages.scrollHeight;
    }

    toggleMinimize() {
        this.isMinimized = !this.isMinimized;
        this.widget.classList.toggle('minimized', this.isMinimized);
        this.minimizeBtn.textContent = this.isMinimized ? '+' : '−';
        if (this.fab) {
            if (this.isMinimized) {
                this.fab.style.display = 'flex';
                this.fab.classList.add('pulse');
            } else {
                this.fab.classList.remove('pulse');
                this.fab.style.display = 'none';
            }
        }
    }

    hideWidget() {
        this.widget.classList.add('hidden');
        if (this.fab) {
            this.fab.style.display = 'flex';
            this.fab.classList.add('pulse');
        }
    }

    showWidget() {
        this.widget.classList.remove('hidden');
        if (this.fab) {
            this.fab.classList.remove('pulse');
            this.fab.style.display = 'none';
        }
    }

    async loadChatHistory() {
        try {
            const response = await fetch('/api/chat/history/');
            const data = await response.json();
            
            if (data.success && data.messages.length > 0) {
                // Clear the welcome message
                this.messages.innerHTML = '';
                
                // Load all messages
                data.messages.forEach(msg => {
                    this.addMessage(msg.type, msg.content, msg.referenced_properties);
                });
                
                this.sessionId = data.session_id;
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }

    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }
}

// Initialize chat widget when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only show chat widget on buyer pages (not seller pages)
    if (!window.location.pathname.startsWith('/seller')) {
        new ChatWidget();
    }
});
