const chatContainer = document.getElementById('chat-container');
const terminalLogs = document.getElementById('terminal-logs');
const terminalLogsBottom = document.getElementById('terminal-logs-bottom');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
// const modelBadge = document.getElementById('model-badge');
const micStatus = document.getElementById('mic-status');

const browserWindow = document.getElementById('browser-window');
const browserIframe = document.getElementById('browser-iframe');
const closeBrowserBtn = document.getElementById('close-browser-btn');
const openExternalBtn = document.getElementById('open-external-btn');

const imagePopup = document.getElementById('image-popup');
const popupImg = document.getElementById('popup-img');
const closeImageBtn = document.getElementById('close-image-btn');
const openImageBtn = document.getElementById('open-image-btn');

function addLog(msg) {
    const time = new Date().toLocaleTimeString();
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    entry.innerHTML = `<span class="log-time">[${time}]</span> ${msg}`;
    terminalLogs.appendChild(entry);
    terminalLogs.scrollTop = terminalLogs.scrollHeight;

    // Mirror to Bottom Terminal if it exists
    if (typeof terminalLogsBottom !== 'undefined' && terminalLogsBottom) {
        const entryBottom = entry.cloneNode(true);
        terminalLogsBottom.appendChild(entryBottom);
        terminalLogsBottom.scrollTop = terminalLogsBottom.scrollHeight;
    }
}

function addMessage(sender, text, isAI = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `msg ${isAI ? 'ai-msg' : 'user-msg'}`;
    msgDiv.innerHTML = `<span class="prefix">${sender}:</span> <span class="text">${text}</span>`;
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text) return;

    addMessage('YOU', text, false);
    messageInput.value = '';
    messageInput.style.height = 'auto';

    addLog(`INITIATING COMMAND: ${text}`);

    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let aiMsgDiv = null;
    let fullText = "";

    while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        if (!aiMsgDiv) {
            aiMsgDiv = document.createElement('div');
            aiMsgDiv.className = 'msg ai-msg';
            aiMsgDiv.innerHTML = `<span class="prefix">TERRY:</span> <span class="text"></span>`;
            chatContainer.appendChild(aiMsgDiv);
        }

        fullText += chunk;
        aiMsgDiv.querySelector('.text').innerText = fullText;
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Update Status from Server
async function fetchUpdates() {
    try {
        const response = await fetch('/api/update');
        const data = await response.json();

        // if (data.model) {
        //    modelBadge.innerText = `MODEL: ${data.model.toUpperCase()}`;
        // }


        // Update Voice Status Toggle (Visual only)
        document.getElementById('voice-status').innerText = data.voice_enabled ? "ON" : "OFF";
        document.getElementById('voice-status').className = data.voice_enabled ? "status-tag" : "status-tag off";

        // --- UPDATE AVATAR STATUS ---
        const avatar = document.getElementById('reactor-core');
        if (avatar) {
            avatar.classList.remove('idle', 'thinking', 'speaking');
            avatar.classList.add(data.status || 'idle');
        }

        if (data.system_stats) {
            document.getElementById('sys-os').innerText = data.system_stats.os;
            document.getElementById('sys-cpu-model').innerText = data.system_stats.processor;
            document.getElementById('sys-cpu-load').innerText = data.system_stats.cpu_load + "%";
            document.getElementById('sys-gpu-name').innerText = data.system_stats.gpu_name; // Bind GPU
            document.getElementById('sys-ram-load').innerText = data.system_stats.ram_load + "%";
            document.getElementById('sys-ram-detail').innerText = `(${data.system_stats.ram_display})`;
        }

        if (data.logs && data.logs.length > 0) {
            // We only want to append NEW logs to avoid flickering or clearing local logs
            // Ideally backend sends only new logs, but for now we can just check the last one?
            // Simpler: Just refresh the bottom terminal completely from server state to match "Tail -f" behavior
            // But KEEP the left terminal local-only or mixed?
            // Let's make Bottom Terminal purely SERVER logs (System Output)

            if (terminalLogsBottom) {
                terminalLogsBottom.innerHTML = '';
                data.logs.forEach(logMsg => {
                    const entry = document.createElement('div');
                    entry.className = 'log-entry';
                    // Parse Timestamp [HH:MM:SS] using regex
                    const timeRegex = /^(\[\d{2}:\d{2}:\d{2}\])\s*(.*)/;
                    const match = logMsg.match(timeRegex);

                    if (match) {
                        const timePart = match[1];
                        const msgPart = match[2];
                        entry.innerHTML = `<span class="log-time">${timePart}</span> ${msgPart}`;
                    } else {
                        entry.innerText = logMsg;
                    }
                    terminalLogsBottom.appendChild(entry);
                });
                terminalLogsBottom.scrollTop = terminalLogsBottom.scrollHeight;
            }
        }


        if (data.url_to_open) {
            addLog(`[DEBUG] FE RECVD URL: ${data.url_to_open}`);
            addLog(`OPENING INTERFACE: ${data.url_to_open}`);
            const browserIframe = document.getElementById('browser-iframe');
            const browserWindow = document.getElementById('browser-window');
            if (browserIframe && browserWindow) {
                browserIframe.src = data.url_to_open;
                browserWindow.style.display = 'flex';
            } else {
                addLog("[ERR] Browser elements not found via ID!");
            }
        }

        if (data.image_to_show) {
            addLog(`[VISUAL] Receiving Image Signal: ${data.image_to_show}`);
            if (imagePopup && popupImg) {
                popupImg.src = data.image_to_show;
                imagePopup.style.display = 'flex';
                addLog(`[VISUAL] Displaying Popup...`);
            } else {
                addLog(`[ERR] Image Popup Elements NOT FOUND!`);
                console.error("Popup elements missing:", { imagePopup, popupImg });
            }
        }

        // Update Voice Button
        const micBtn = document.getElementById('mic-toggle-btn');
        if (micBtn && data.voice_enabled !== undefined) {
            if (data.voice_enabled) {
                micBtn.innerText = "MIC: ON";
                micBtn.classList.add("active");
                micBtn.classList.remove("inactive");
            } else {
                micBtn.innerText = "MIC: OFF";
                micBtn.classList.add("inactive");
                micBtn.classList.remove("active");
            }
        }

    } catch (e) {
        console.error("Fetch Error:", e);
        if (typeof addLog === "function") {
            addLog(`SYS_ERR: Fetch failed - ${e}`);
        }
    }
}

async function toggleMic() {
    try {
        await fetch('/api/toggle_voice', { method: 'POST' });
    } catch (e) {
        addLog(`ERR: Toggle Mic failed - ${e}`);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initVisualizer();
    setInterval(fetchUpdates, 1000);
});

function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    const dateString = now.toLocaleDateString();

    // Update new top bar clock
    const sysTime = document.getElementById('sys-time');
    if (sysTime) sysTime.innerText = timeString + " " + dateString;
}

setInterval(updateClock, 1000);
updateClock();
closeBrowserBtn.addEventListener('click', () => {
    browserWindow.style.display = 'none';
    browserIframe.src = '';
});

openExternalBtn.addEventListener('click', () => {
    if (browserIframe.src) window.open(browserIframe.src, '_blank');
});

// Draggable Mini Browser
function makeDraggable(el, handle) {
    let x = 0, y = 0, nx = 0, ny = 0;
    handle.onmousedown = (e) => {
        e.preventDefault();
        nx = e.clientX; ny = e.clientY;
        document.onmouseup = () => { document.onmouseup = null; document.onmousemove = null; };
        document.onmousemove = (e) => {
            x = nx - e.clientX; y = ny - e.clientY;
            nx = e.clientX; ny = e.clientY;
            el.style.top = (el.offsetTop - y) + "px";
            el.style.left = (el.offsetLeft - x) + "px";
        };
    };
}
makeDraggable(browserWindow, browserWindow.querySelector('.browser-header'));

// Image Popup Events
// v2.3 Updated
if (closeImageBtn) {
    closeImageBtn.addEventListener('click', () => {
        imagePopup.style.display = 'none';
        popupImg.src = '';
    });
}

if (openImageBtn) {
    openImageBtn.addEventListener('click', () => {
        if (popupImg.src) window.open(popupImg.src, '_blank');
    });
}

if (imagePopup) {
    makeDraggable(imagePopup, imagePopup.querySelector('.browser-header'));
}

addLog("SYSTEM_BOOT: SUCCESSFUL");
addLog(" Terry OS Mark II Initialized...");

// --- CIRCULAR VISUALIZER GENERATION ---
function initVisualizer() {
    const visualizer = document.getElementById('voice-visualizer');
    if (!visualizer) return;

    const barCount = 40;
    for (let i = 0; i < barCount; i++) {
        const bar = document.createElement('div');
        bar.className = 'visualizer-bar';

        // Arrange in a circle
        const rotation = (i / barCount) * 360;
        bar.style.transform = `translate(-50%, -50%) rotate(${rotation}deg)`;

        // Random animation delay and height variable for organic feel
        const delay = Math.random() * 0.5;
        const h = 25 + Math.random() * 25;
        bar.style.animationDelay = `${delay}s`;
        bar.style.setProperty('--h', `${h}px`);

        visualizer.appendChild(bar);
    }
}
