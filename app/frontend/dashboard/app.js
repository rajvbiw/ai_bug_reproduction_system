const API_BASE = "http://localhost:8085/api/v1";

// DOM Elements
const navItems = document.querySelectorAll('.nav-item');
const views = document.querySelectorAll('.content-view');
const bugForm = document.getElementById('bug-form');
const bugsTableBody = document.querySelector('#bugs-table tbody');
const refreshBtn = document.getElementById('refresh-btn');
const toastContainer = document.getElementById('toast-container');

// Stats Elements
const totalBugsEl = document.getElementById('total-bugs');
const inProgressEl = document.getElementById('in-progress');
const reproducedEl = document.getElementById('reproduced');
const failedEl = document.getElementById('failed');

// Modal Elements
const detailsModal = document.getElementById('details-modal');
const modalCloseBtn = document.getElementById('modal-close-btn');
const modalBugTitle = document.getElementById('modal-bug-title');
const modalBugBody = document.getElementById('modal-bug-body');

// Chat Elements
const chatHistoryContainer = document.getElementById('chat-history-container');
const chatInput = document.getElementById('chat-input');
const chatSendBtn = document.getElementById('chat-send-btn');
const chatMicBtn = document.getElementById('chat-mic-btn');
const chatModelSelect = document.getElementById('chat-model-select');
const clearChatBtn = document.getElementById('clear-chat-btn');
const modeAssistantBtn = document.getElementById('mode-assistant');
const modeAnalysisBtn = document.getElementById('mode-analysis');

// Log Analyzer Elements
const analyzeTextBtn = document.getElementById('analyze-text-btn');
const logTextInput = document.getElementById('log-text-input');
const logFileDrop = document.getElementById('log-file-drop');
const logFileInput = document.getElementById('log-file-input');
const analyzeFileBtn = document.getElementById('analyze-file-btn');
const ocrDrop = document.getElementById('ocr-drop');
const ocrFileInput = document.getElementById('ocr-file-input');
const analyzeOcrBtn = document.getElementById('analyze-ocr-btn');

// Log Analysis Results
const resultsSeverity = document.getElementById('results-severity');
const resultSummary = document.getElementById('result-summary');
const resultCause = document.getElementById('result-cause');
const resultFixes = document.getElementById('result-fixes');
const resultPatch = document.getElementById('result-patch');
const resultOcrText = document.getElementById('result-ocr-text');
const extractedTextSection = document.getElementById('extracted-text-section');

// GitHub Elements
const githubForm = document.getElementById('github-form');
const githubResults = document.getElementById('github-results');
const githubStatusBox = document.getElementById('github-status-box');

// Settings Elements
const settingsForm = document.getElementById('settings-form');

// State
let bugs = [];
let reports = [];
let conversationId = "";
let selectedChatMode = "debugger"; // debugger or analyzer
let activeLogFile = null;
let activeOcrFile = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupNavigation();
    setupConversation();
    fetchBugs();
    setupForm();
    setupChat();
    setupAnalyzer();
    setupGithub();
    setupSettings();
    setupModal();
    
    // Auto refresh bug list every 15 seconds
    setInterval(fetchBugs, 15000);
});

// Setup Unique Conversation ID
function setupConversation() {
    conversationId = localStorage.getItem('chat_conversation_id');
    if (!conversationId) {
        conversationId = 'conv_' + Math.random().toString(36).substring(2, 15);
        localStorage.setItem('chat_conversation_id', conversationId);
    }
    loadChatHistory();
}

// Navigation Logic
function setupNavigation() {
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const viewId = item.getAttribute('data-view');
            
            // Update Active Nav
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            
            // Switch View
            views.forEach(view => {
                view.classList.remove('active');
                if (view.id === `${viewId}-view`) {
                    view.classList.add('active');
                }
            });

            if (viewId === 'reports') {
                fetchReports();
            }
        });
    });
}

// Fetch Bugs API
async function fetchBugs() {
    try {
        const response = await fetch(`${API_BASE}/bugs/`);
        if (!response.ok) throw new Error('Failed to fetch bugs');
        
        bugs = await response.json();
        updateUI();
    } catch (error) {
        showToast('Error', error.message, 'error');
    }
}

// Submit New Bug Report
async function submitBug(data) {
    try {
        const response = await fetch(`${API_BASE}/bugs/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) throw new Error('Failed to submit bug report');
        
        const newBug = await response.json();
        bugs.unshift(newBug);
        updateUI();
        showToast('Success', 'Bug report submitted and reproduction started!', 'success');
        
        // Switch back to dashboard
        document.querySelector('[data-view="dashboard"]').click();
        bugForm.reset();
    } catch (error) {
        showToast('Error', error.message, 'error');
    }
}

// UI Rendering
function updateUI() {
    renderTable();
    updateStats();
    lucide.createIcons();
}

function renderTable() {
    bugsTableBody.innerHTML = '';
    
    if (bugs.length === 0) {
        bugsTableBody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 2rem; color: var(--text-muted);">No bug reports found.</td></tr>';
        return;
    }

    bugs.forEach(bug => {
        const row = document.createElement('tr');
        const statusClass = getStatusClass(bug.status);
        const date = new Date(bug.created_at).toLocaleDateString();
        
        row.innerHTML = `
            <td>
                <div style="display: flex; flex-direction: column;">
                    <span style="font-weight: 600;">${bug.title}</span>
                    <span style="font-size: 0.75rem; color: var(--text-muted);">${bug.repository_url || 'No repo provided'}</span>
                </div>
            </td>
            <td><span class="status-tag ${statusClass}">${bug.status}</span></td>
            <td>${date}</td>
            <td>${bug.reproduction_duration || '--'}</td>
            <td>
                <button class="btn view-details-btn" style="padding: 6px; background: var(--glass-bg);" title="View Details" data-id="${bug.id}">
                    <i data-lucide="eye" style="width: 16px; height: 16px;"></i>
                </button>
            </td>
        `;
        bugsTableBody.appendChild(row);
    });

    // Add listeners to detail buttons
    document.querySelectorAll('.view-details-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const bugId = btn.getAttribute('data-id');
            showBugDetails(bugId);
        });
    });
}

function updateStats() {
    totalBugsEl.textContent = bugs.length;
    inProgressEl.textContent = bugs.filter(b => b.status === 'analyzing' || b.status === 'reproducing').length;
    reproducedEl.textContent = bugs.filter(b => b.status === 'reproduced').length;
    failedEl.textContent = bugs.filter(b => b.status === 'failed' || b.status === 'not_reproduced').length;
}

function getStatusClass(status) {
    status = status.toLowerCase();
    if (status === 'analyzing' || status === 'reproducing') return 'in-progress';
    if (status === 'reproduced') return 'success';
    if (status === 'failed' || status === 'not_reproduced') return 'failed';
    return '';
}

// Form logic
function setupForm() {
    bugForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = {
            title: document.getElementById('title').value,
            description: document.getElementById('description').value,
            repository_url: document.getElementById('repository_url').value,
            target_branch: document.getElementById('target_branch').value
        };
        submitBug(formData);
    });
}

// Chat Implementation
function setupChat() {
    // Mode toggles
    modeAssistantBtn.addEventListener('click', () => {
        selectedChatMode = "debugger";
        modeAssistantBtn.classList.add('active');
        modeAnalysisBtn.classList.remove('active');
    });

    modeAnalysisBtn.addEventListener('click', () => {
        selectedChatMode = "analyzer";
        modeAnalysisBtn.classList.add('active');
        modeAssistantBtn.classList.remove('active');
    });

    // Send Button click
    chatSendBtn.addEventListener('click', sendChatMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });

    // Clear Chat click
    clearChatBtn.addEventListener('click', async () => {
        if (confirm("Are you sure you want to clear chat history?")) {
            try {
                const response = await fetch(`${API_BASE}/chat/history/${conversationId}`, { method: 'DELETE' });
                if (response.ok) {
                    chatHistoryContainer.innerHTML = '<div class="chat-message assistant"><div class="message-content">Conversation cleared. What can I debug next?</div></div>';
                    showToast("Success", "Conversation history cleared", "success");
                }
            } catch (err) {
                showToast("Error", err.message, "error");
            }
        }
    });

    // Voice Input Speech Recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        let isRecording = false;

        chatMicBtn.addEventListener('click', () => {
            if (!isRecording) {
                recognition.start();
            } else {
                recognition.stop();
            }
        });

        recognition.onstart = () => {
            isRecording = true;
            chatMicBtn.classList.add('recording');
            chatMicBtn.style.color = '#ff453a';
            showToast("Voice", "Listening...", "info");
        };

        recognition.onend = () => {
            isRecording = false;
            chatMicBtn.classList.remove('recording');
            chatMicBtn.style.color = 'var(--text-muted)';
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            chatInput.value = transcript;
            showToast("Voice Recognized", transcript, "success");
        };

        recognition.onerror = (e) => {
            showToast("Speech Error", e.error, "error");
        };
    } else {
        chatMicBtn.style.display = 'none';
    }
}

async function loadChatHistory() {
    try {
        const response = await fetch(`${API_BASE}/chat/history/${conversationId}`);
        if (!response.ok) return;
        
        const history = await response.json();
        chatHistoryContainer.innerHTML = '';
        
        if (history.length === 0) {
            chatHistoryContainer.innerHTML = '<div class="chat-message assistant"><div class="message-content">Hello! I am your AI Debugging Assistant. How can I help you reproduce and debug your bugs today?</div></div>';
            return;
        }

        history.forEach(msg => {
            appendMessageToContainer(msg.role, msg.content);
        });
        scrollToBottom();
    } catch (error) {
        console.error("Failed to load chat history:", error);
    }
}

function appendMessageToContainer(role, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message ${role}`;
    const contentDiv = document.createElement('div');
    contentDiv.className = "message-content";
    contentDiv.innerHTML = marked.parse(text);
    msgDiv.appendChild(contentDiv);
    chatHistoryContainer.appendChild(msgDiv);
}

function scrollToBottom() {
    chatHistoryContainer.scrollTop = chatHistoryContainer.scrollHeight;
}

async function sendChatMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    // Append user message
    appendMessageToContainer('user', text);
    chatInput.value = '';
    scrollToBottom();

    // Create assistant streaming block
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message assistant`;
    const contentDiv = document.createElement('div');
    contentDiv.className = "message-content";
    contentDiv.innerHTML = "Thinking...";
    msgDiv.appendChild(contentDiv);
    chatHistoryContainer.appendChild(msgDiv);
    scrollToBottom();

    const systemPrompt = selectedChatMode === "debugger" 
        ? "You are an expert Python Debugging Assistant. Help the user debug their test failures, logs, or codebase. Output markdown."
        : "You are an expert Log & Stack Trace Analyzer. Analyze tracebacks or bugs specifically identifying exact exception causes, file lines and suggesting quick patches.";

    try {
        const response = await fetch(`${API_BASE}/chat/stream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                conversation_id: conversationId,
                message: text,
                system_prompt: systemPrompt
            })
        });

        if (!response.ok) throw new Error("Streaming error");

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullResponse = "";
        contentDiv.innerHTML = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value);
            fullResponse += chunk;
            contentDiv.innerHTML = marked.parse(fullResponse);
            scrollToBottom();
        }
    } catch (err) {
        contentDiv.innerHTML = `<span style="color: var(--red-glow);">Error: ${err.message}</span>`;
    }
}

// Log Analyzer Tab & Inputs
function setupAnalyzer() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === tabId) {
                    content.classList.add('active');
                }
            });
        });
    });

    // Paste Text Analyze
    analyzeTextBtn.addEventListener('click', async () => {
        const text = logTextInput.value.trim();
        if (!text) {
            showToast("Error", "Please paste log content", "error");
            return;
        }
        analyzeTextBtn.disabled = true;
        analyzeTextBtn.innerHTML = '<i data-lucide="loader" class="spin"></i> Analyzing...';
        lucide.createIcons();

        try {
            const response = await fetch(`${API_BASE}/analyze/log`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ logs: text })
            });
            if (!response.ok) throw new Error("Analysis failed");
            const data = await response.json();
            renderAnalysisResults(data);
            showToast("Success", "Analysis complete!", "success");
        } catch (err) {
            showToast("Error", err.message, "error");
        } finally {
            analyzeTextBtn.disabled = false;
            analyzeTextBtn.innerHTML = '<i data-lucide="search-code"></i> Run Log Analysis';
            lucide.createIcons();
        }
    });

    // Drag-Drop File Upload
    setupDropZone(logFileDrop, logFileInput, (file) => {
        activeLogFile = file;
        analyzeFileBtn.disabled = false;
        logFileDrop.querySelector('p').textContent = `Loaded: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
        showToast("File Loaded", file.name, "success");
    });

    analyzeFileBtn.addEventListener('click', async () => {
        if (!activeLogFile) return;
        analyzeFileBtn.disabled = true;
        analyzeFileBtn.innerHTML = '<i data-lucide="loader" class="spin"></i> Running...';
        lucide.createIcons();

        const formData = new FormData();
        formData.append("file", activeLogFile);

        try {
            const response = await fetch(`${API_BASE}/analyze/log-file`, {
                method: 'POST',
                body: formData
            });
            if (!response.ok) throw new Error("Analysis failed");
            const data = await response.json();
            renderAnalysisResults(data);
            showToast("Success", "Analysis complete!", "success");
        } catch (err) {
            showToast("Error", err.message, "error");
        } finally {
            analyzeFileBtn.disabled = false;
            analyzeFileBtn.innerHTML = '<i data-lucide="play-circle"></i> Analyze File';
            lucide.createIcons();
        }
    });

    // Drag-Drop Screenshot Upload (OCR)
    setupDropZone(ocrDrop, ocrFileInput, (file) => {
        activeOcrFile = file;
        analyzeOcrBtn.disabled = false;
        ocrDrop.querySelector('p').textContent = `Loaded Image: ${file.name}`;
        showToast("Image Loaded", file.name, "success");
    });

    analyzeOcrBtn.addEventListener('click', async () => {
        if (!activeOcrFile) return;
        analyzeOcrBtn.disabled = true;
        analyzeOcrBtn.innerHTML = '<i data-lucide="loader" class="spin"></i> Processing OCR...';
        lucide.createIcons();

        const formData = new FormData();
        formData.append("file", activeOcrFile);

        try {
            const response = await fetch(`${API_BASE}/analyze/screenshot`, {
                method: 'POST',
                body: formData
            });
            if (!response.ok) throw new Error("Analysis failed");
            const data = await response.json();
            renderAnalysisResults(data);
            showToast("Success", "Screenshot OCR complete!", "success");
        } catch (err) {
            showToast("Error", err.message, "error");
        } finally {
            analyzeOcrBtn.disabled = false;
            analyzeOcrBtn.innerHTML = '<i data-lucide="scan-eye"></i> Run OCR & Analysis';
            lucide.createIcons();
        }
    });
}

function setupDropZone(dropZone, fileInput, callback) {
    dropZone.addEventListener('click', () => fileInput.click());
    
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            callback(fileInput.files[0]);
        }
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--primary)';
        dropZone.style.background = 'rgba(138, 43, 226, 0.05)';
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZone.style.borderColor = 'var(--glass-border)';
            dropZone.style.background = 'transparent';
        });
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        if (dt.files.length > 0) {
            callback(dt.files[0]);
        }
    });
}

function renderAnalysisResults(data) {
    // Severity tag
    const severity = data.severity || "Medium";
    resultsSeverity.textContent = severity;
    resultsSeverity.className = `severity-badge ${severity.toLowerCase()}`;

    // Text fields
    resultSummary.innerHTML = marked.parse(data.summary || "--");
    resultCause.textContent = data.root_cause || "--";

    // Fixes
    resultFixes.innerHTML = '';
    const fixes = data.suggested_fix || [];
    if (Array.isArray(fixes)) {
        fixes.forEach(fix => {
            const li = document.createElement('li');
            li.textContent = fix;
            resultFixes.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.textContent = fixes;
        resultFixes.appendChild(li);
    }

    // Patch
    resultPatch.textContent = data.patch_example || "# No code patch generated";

    // OCR Text
    if (data.extracted_text) {
        extractedTextSection.style.display = 'block';
        resultOcrText.textContent = data.extracted_text;
    } else {
        extractedTextSection.style.display = 'none';
    }
}

// GitHub Form Importer
function setupGithub() {
    githubForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const submitBtn = document.getElementById('github-submit-btn');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i data-lucide="loader" class="spin"></i> Syncing...';
        lucide.createIcons();

        const repoUrl = document.getElementById('github-repo').value;
        const issueNum = document.getElementById('github-issue-number').value;

        try {
            const response = await fetch(`${API_BASE}/github/import`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    repo_url: repoUrl,
                    issue_number: parseInt(issueNum)
                })
            });

            if (!response.ok) throw new Error("Sync failure");
            const data = await response.json();
            
            githubResults.style.display = 'block';
            githubStatusBox.innerHTML = `
                <div style="display:flex; justify-content:space-between; margin-bottom:1rem;">
                    <strong>Bug Title:</strong> <span>${data.bug_report.title}</span>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:1rem;">
                    <strong>Status:</strong> <span class="status-tag success">${data.bug_report.status}</span>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:1rem;">
                    <strong>Github URL:</strong> <a href="https://github.com/${repoUrl.replace("https://github.com/", "")}/issues/${issueNum}" target="_blank">View Issue</a>
                </div>
                <h4 style="margin-top:1.5rem; margin-bottom:0.5rem; color:var(--primary);">AI Reproduction Plan</h4>
                <p><strong>Expected:</strong> ${data.reproduction_plan.expected_behavior}</p>
                <p><strong>Actual:</strong> ${data.reproduction_plan.actual_behavior}</p>
                <p><strong>Reproduction steps:</strong></p>
                <ul>
                    ${data.reproduction_plan.reproduction_steps.map(step => `<li>${step}</li>`).join('')}
                </ul>
            `;
            showToast("GitHub Synced", `Imported issue #${issueNum}`, "success");
            githubForm.reset();
            fetchBugs();
        } catch (err) {
            showToast("Error", err.message, "error");
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i data-lucide="download-cloud"></i> Import & Auto-Analyze';
            lucide.createIcons();
        }
    });
}

// Fetch Reports History
async function fetchReports() {
    const tableBody = document.querySelector('#reports-history-table tbody');
    tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 2rem;">Loading reports history...</td></tr>';

    try {
        const response = await fetch(`${API_BASE}/bugs/`);
        if (!response.ok) throw new Error();
        
        const bugsData = await response.json();
        reports = bugsData; // Using bug records to map to analyses
        
        tableBody.innerHTML = '';
        if (reports.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 2rem; color: var(--text-muted);">No reports found.</td></tr>';
            return;
        }

        reports.forEach(bug => {
            const row = document.createElement('tr');
            const date = new Date(bug.created_at).toLocaleDateString();
            
            row.innerHTML = `
                <td><strong>${bug.title}</strong></td>
                <td><span class="severity-badge medium">Medium</span></td>
                <td><span style="font-size: 0.85rem; color: var(--text-muted);">${bug.description.substring(0, 80)}...</span></td>
                <td>${date}</td>
                <td>
                    <button class="btn report-details-btn" style="padding: 6px; background: var(--glass-bg);" title="View Summary" data-id="${bug.id}">
                        <i data-lucide="file-search" style="width: 16px; height: 16px;"></i>
                    </button>
                </td>
            `;
            tableBody.appendChild(row);
        });

        document.querySelectorAll('.report-details-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.getAttribute('data-id');
                showBugDetails(id);
            });
        });
        lucide.createIcons();
    } catch (err) {
        tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 2rem; color: var(--red-glow);">Failed to fetch reports.</td></tr>';
    }
}

// Settings Integration
function setupSettings() {
    // Load config from LocalStorage
    const oUrl = localStorage.getItem('config_ollama_url') || 'http://localhost:11434';
    const oModel = localStorage.getItem('config_ollama_model') || 'llama3';
    const slackWeb = localStorage.getItem('config_slack_webhook') || '';
    const githubTok = localStorage.getItem('config_github_token') || '';

    document.getElementById('settings-ollama-url').value = oUrl;
    document.getElementById('settings-ollama-model').value = oModel;
    document.getElementById('settings-slack-webhook').value = slackWeb;
    document.getElementById('settings-github-token').value = githubTok;

    settingsForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const urlVal = document.getElementById('settings-ollama-url').value.trim();
        const modelVal = document.getElementById('settings-ollama-model').value.trim();
        const webhookVal = document.getElementById('settings-slack-webhook').value.trim();
        const tokenVal = document.getElementById('settings-github-token').value.trim();

        localStorage.setItem('config_ollama_url', urlVal);
        localStorage.setItem('config_ollama_model', modelVal);
        localStorage.setItem('config_slack_webhook', webhookVal);
        localStorage.setItem('config_github_token', tokenVal);

        showToast("Success", "Settings saved locally!", "success");
    });
}

// Modal handling
function setupModal() {
    modalCloseBtn.addEventListener('click', () => {
        detailsModal.style.display = 'none';
    });
    
    window.addEventListener('click', (e) => {
        if (e.target === detailsModal) {
            detailsModal.style.display = 'none';
        }
    });
}

async function showBugDetails(bugId) {
    detailsModal.style.display = 'flex';
    modalBugTitle.textContent = "Loading Details...";
    modalBugBody.innerHTML = '<div style="text-align: center; padding: 3rem;"><i data-lucide="loader" class="spin" style="width: 32px; height: 32px;"></i></div>';
    lucide.createIcons();

    try {
        // Fetch bug details (we look up from our local bugs array first)
        const bug = bugs.find(b => b.id == bugId) || reports.find(b => b.id == bugId);
        if (!bug) throw new Error("Bug report not found");

        modalBugTitle.textContent = bug.title;
        
        let detailsHtml = `
            <div class="modal-section">
                <h4>Description</h4>
                <p>${bug.description}</p>
            </div>
            <div class="modal-section">
                <h4>Repository Details</h4>
                <p>URL: <a href="${bug.repository_url || '#'}" target="_blank">${bug.repository_url || 'No repository provided'}</a></p>
                <p>Environment: ${bug.environment_details || 'N/A'}</p>
            </div>
            <div class="modal-section">
                <h4>Reproduction Plan (AI Generated)</h4>
                <pre><code>${bug.steps_to_reproduce || 'Analyzing Steps...'}</code></pre>
            </div>
            <div class="modal-section">
                <h4>Expected vs Actual</h4>
                <p><strong>Expected:</strong> ${bug.expected_behavior || 'N/A'}</p>
                <p><strong>Actual:</strong> ${bug.actual_behavior || 'N/A'}</p>
            </div>
            <div class="modal-section">
                <h4>Reproduction Status</h4>
                <span class="status-tag ${getStatusClass(bug.status)}">${bug.status}</span>
            </div>
        `;
        
        modalBugBody.innerHTML = detailsHtml;
        lucide.createIcons();
    } catch (err) {
        modalBugTitle.textContent = "Error";
        modalBugBody.innerHTML = `<p style="color: var(--red-glow);">${err.message}</p>`;
    }
}

// Notifications
function showToast(title, message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <strong>${title}</strong>
            <span>${message}</span>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    toast.style.cssText = `
        background: var(--card-bg);
        border-left: 4px solid ${type === 'error' ? '#ff453a' : type === 'success' ? '#00ff7f' : 'var(--primary)'};
        padding: 1rem;
        margin-bottom: 0.5rem;
        border-radius: 8px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        animation: slideIn 0.3s ease-out;
        color: white;
        min-width: 250px;
    `;
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(20px)';
        toast.style.transition = 'all 0.3s ease-in';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}
