const chatContainer = document.getElementById('chat-container');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const terminalLogs = document.getElementById('terminal-logs');
const modelBadge = document.getElementById('model-badge');
const modelSelect = document.getElementById('model-select');

// --- Sidebar Resizer Logic ---
const sidebar = document.getElementById('sidebar');
const resizer = document.getElementById('resizer');

// Restore saved width
const savedWidth = localStorage.getItem('sidebarWidth');
if (savedWidth) {
    sidebar.style.width = savedWidth + 'px';
}

resizer.addEventListener('mousedown', function (e) {
    e.preventDefault();
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', stopResizing);
    resizer.classList.add('resizing');
});

function handleMouseMove(e) {
    const newWidth = e.clientX;
    if (newWidth > 150 && newWidth < window.innerWidth * 0.8) {
        sidebar.style.width = newWidth + 'px';
        localStorage.setItem('sidebarWidth', newWidth);
    }
}

function stopResizing() {
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', stopResizing);
    resizer.classList.remove('resizing');
}

// --- Settings Logic ---
modelSelect.addEventListener('change', async function () {
    const selectedModel = this.value;
    try {
        await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model_name: selectedModel })
        });
        console.log("Model changed to:", selectedModel);
    } catch (err) {
        console.error("Failed to change settings:", err);
    }
});

// Auto-resize textarea
messageInput.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

// Submit on Enter (Shift+Enter for new line)
messageInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendBtn.addEventListener('click', sendMessage);

// --- Polling for Status & Logs ---
async function fetchUpdates() {
    try {
        const response = await fetch('/api/update');
        const data = await response.json();

        // 1. Update Model
        if (data.model) {
            modelBadge.innerText = `Model: ${data.model}`;
        }

        // 1b. Sync Dropdown (if exists and value differs)
        if (data.perplexity_model && modelSelect.value !== data.perplexity_model) {
            // Only update if not currently focused (to avoid annoying jumps while selecting)
            if (document.activeElement !== modelSelect) {
                modelSelect.value = data.perplexity_model;
            }
        }

        // 2. Update Logs
        terminalLogs.innerHTML = '';
        data.logs.forEach(log => {
            const div = document.createElement('div');
            div.className = 'log-entry';
            div.textContent = log;
            terminalLogs.appendChild(div);
        });

        // Auto-scroll logs
        terminalLogs.scrollTop = terminalLogs.scrollHeight;

    } catch (err) {
        console.error("Failed to fetch updates:", err);
    }
}

// Poll every 1 second
setInterval(fetchUpdates, 1000);
fetchUpdates(); // Initial call

// --- Chat Logic ---

async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text) return;

    // Reset input
    messageInput.value = '';
    messageInput.style.height = 'auto';

    // 1. Add User Message
    addMessage('user', text);

    // 2. Add AI Placeholder
    const aiMessageId = addMessage('ai', '');
    const aiTextElement = document.getElementById(aiMessageId).querySelector('.text');
    let aiResponse = "";

    // 3. Fetch Stream
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            aiResponse += chunk;

            // Simple Markdown Image Renderer
            // Regex detects ![Alt](/path/to/img) and converts to <img src="...">
            const htmlResponse = aiResponse
                .replace(/\n/g, '<br>')
                .replace(/!\[(.*?)\]\((.*?)\)/g, '<img src="$2" alt="$1" class="chat-image">');

            aiTextElement.innerHTML = htmlResponse;

            // Auto scroll main chat
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

    } catch (err) {
        aiTextElement.innerText = "Error: " + err.message;
    }
}

function addMessage(role, text) {
    const id = 'msg-' + Date.now();
    const div = document.createElement('div');
    div.className = `message-row ${role}`;
    div.id = id;

    // Avatar
    const avatar = role === 'user' ? 'U' : 'T';

    div.innerHTML = `
        <div class="message-content">
            <div class="avatar ${role}">${avatar}</div>
            <div class="text">${text}</div>
        </div>
    `;

    chatContainer.appendChild(div);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    return id;
}
