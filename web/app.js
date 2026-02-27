/* ═══════════════════════════════════════════════════════════════
   AUTONOMOUS AGENT — Frontend JavaScript
   Handles: provider config, SSE streaming, log rendering, markdown
   ═══════════════════════════════════════════════════════════════ */

// ─── State ──────────────────────────────────────────────────────
let selectedDepth = 'detailed';
let isRunning = false;
let reportContent = '';

// ─── Init ───────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    loadProviders();
    setupDepthSelector();
    createParticles();
});

// ─── Background Particles ───────────────────────────────────────
function createParticles() {
    const container = document.getElementById('particles');
    if (!container) return;
    const count = 35;
    for (let i = 0; i < count; i++) {
        const p = document.createElement('div');
        p.className = 'particle';
        p.style.left = Math.random() * 100 + '%';
        p.style.top = Math.random() * 100 + '%';
        p.style.width = p.style.height = (Math.random() * 3 + 1) + 'px';
        p.style.animationDuration = (Math.random() * 20 + 10) + 's';
        p.style.animationDelay = (Math.random() * 10) + 's';
        p.style.opacity = Math.random() * 0.5 + 0.1;
        container.appendChild(p);
    }
}

// ─── Provider Loading ───────────────────────────────────────────
async function loadProviders() {
    try {
        const resp = await fetch('/api/providers');
        const data = await resp.json();
        const providerSelect = document.getElementById('providerSelect');
        const modelSelect = document.getElementById('modelSelect');

        // Set active provider
        providerSelect.value = data.active_provider;

        // Populate models for active provider
        updateModels(data.providers, data.active_provider);

        // On provider change
        providerSelect.addEventListener('change', () => {
            updateModels(data.providers, providerSelect.value);
        });

        window._providerData = data.providers;
    } catch (e) {
        console.warn('Could not load providers:', e);
    }
}

function updateModels(providers, providerName) {
    const modelSelect = document.getElementById('modelSelect');
    const provider = providers[providerName];
    if (!provider) return;

    modelSelect.innerHTML = '';
    provider.models.forEach(model => {
        const option = document.createElement('option');
        option.value = model;
        option.textContent = model;
        if (model === provider.active_model) option.selected = true;
        modelSelect.appendChild(option);
    });
}

// ─── Depth Selector ─────────────────────────────────────────────
function setupDepthSelector() {
    document.querySelectorAll('.depth-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.depth-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            selectedDepth = btn.dataset.depth;
        });
    });
}

// ─── Goal Setting ───────────────────────────────────────────────
function setGoal(text) {
    document.getElementById('goalInput').value = text;
    document.getElementById('goalInput').focus();
}

// ─── Start Agent ────────────────────────────────────────────────
async function startAgent() {
    const goal = document.getElementById('goalInput').value.trim();
    if (!goal) {
        alert('Please enter a research goal.');
        return;
    }

    const provider = document.getElementById('providerSelect').value;
    const model = document.getElementById('modelSelect').value;

    // Update UI state
    isRunning = true;
    updateUIState('running');
    clearLogs();
    clearReport();

    try {
        // Start the agent
        const resp = await fetch('/api/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ goal, provider, model, depth: selectedDepth }),
        });

        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.error || 'Failed to start agent');
        }

        // Start SSE streaming
        streamLogs();

    } catch (e) {
        addLogEntry('error', `❌ ${e.message}`);
        updateUIState('error');
        isRunning = false;
    }
}

// ─── SSE Log Streaming ──────────────────────────────────────────
function streamLogs() {
    const eventSource = new EventSource('/api/stream');

    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.phase === 'done') {
            // Agent completed
            eventSource.close();
            isRunning = false;
            updateUIState('complete');
            if (data.report) {
                showReport(data.report);
                reportContent = data.report;
            }
            setActivePhase('complete');
            return;
        }

        if (data.phase === 'error') {
            eventSource.close();
            isRunning = false;
            updateUIState('error');
            addLogEntry('error', data.message);
            return;
        }

        if (data.phase === 'heartbeat') return;

        // Add log entry
        addLogEntry(data.phase, data.message);

        // Update phase tracker
        updatePhaseFromLog(data.phase);
    };

    eventSource.onerror = () => {
        eventSource.close();
        if (isRunning) {
            isRunning = false;
            updateUIState('error');
            addLogEntry('error', 'Connection to agent lost.');
        }
    };
}

// ─── Stop Agent ─────────────────────────────────────────────────
async function stopAgent() {
    try {
        await fetch('/api/stop', { method: 'POST' });
    } catch (e) {
        console.warn('Stop request failed:', e);
    }
}

// ─── Log Rendering ──────────────────────────────────────────────
function clearLogs() {
    const container = document.getElementById('logContainer');
    container.innerHTML = '';
}

function addLogEntry(phase, message) {
    const container = document.getElementById('logContainer');
    const placeholder = document.getElementById('logPlaceholder');
    if (placeholder) placeholder.remove();

    const entry = document.createElement('div');
    entry.className = 'log-entry';

    const now = new Date();
    const time = now.toTimeString().slice(0, 8);

    entry.innerHTML = `
        <span class="log-time">${time}</span>
        <span class="log-phase ${phase}">${phase}</span>
        <span class="log-message">${escapeHtml(message)}</span>
    `;

    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;

    // Update iteration badge
    const iterMatch = message.match(/ITERATION (\d+)/);
    if (iterMatch) {
        document.getElementById('iterBadge').textContent = `Iteration ${iterMatch[1]}`;
    }
}

// ─── Phase Tracker ──────────────────────────────────────────────
function updatePhaseFromLog(phase) {
    const phaseMap = {
        'init': null,
        'plan': 'plan',
        'execute': 'execute',
        'search': 'execute',
        'extract': 'execute',
        'analyze': 'execute',
        'reflect': 'reflect',
        'synthesize': 'synthesize',
        'complete': 'synthesize',
    };

    const mapped = phaseMap[phase];
    if (mapped) setActivePhase(mapped);
}

function setActivePhase(targetPhase) {
    const phases = ['plan', 'execute', 'reflect', 'synthesize'];
    const targetIdx = phases.indexOf(targetPhase);

    document.querySelectorAll('.phase-step').forEach((el, idx) => {
        el.classList.remove('active', 'completed');
        if (idx < targetIdx) el.classList.add('completed');
        if (idx === targetIdx) el.classList.add('active');
    });

    document.querySelectorAll('.phase-connector').forEach((el, idx) => {
        el.classList.toggle('active', idx < targetIdx);
    });
}

// ─── Report Rendering ───────────────────────────────────────────
function clearReport() {
    const container = document.getElementById('reportContainer');
    container.innerHTML = `
        <div class="report-placeholder">
            <div class="placeholder-icon">📝</div>
            <p>Report will appear here</p>
            <p class="placeholder-sub">The agent will generate a comprehensive research report after completing its autonomous research cycle.</p>
        </div>
    `;
    document.getElementById('reportActions').classList.add('hidden');
}

function showReport(markdown) {
    const container = document.getElementById('reportContainer');
    container.innerHTML = `<div class="report-content">${renderMarkdown(markdown)}</div>`;
    document.getElementById('reportActions').classList.remove('hidden');
    // Show the toggle button on small screens
    const toggleBtn = document.getElementById('reportToggleBtn');
    if (toggleBtn) toggleBtn.classList.remove('hidden');
}

// ─── Simple Markdown Renderer ───────────────────────────────────
function renderMarkdown(md) {
    let html = escapeHtml(md);

    // Headers
    html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');

    // Bold & Italic
    html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

    // Code
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Tables
    html = html.replace(/^(\|.+\|)\n(\|[-| :]+\|)\n((?:\|.+\|\n?)*)/gm, (match, header, sep, body) => {
        const headers = header.split('|').filter(c => c.trim()).map(c => `<th>${c.trim()}</th>`).join('');
        const rows = body.trim().split('\n').map(row => {
            const cells = row.split('|').filter(c => c.trim()).map(c => `<td>${c.trim()}</td>`).join('');
            return `<tr>${cells}</tr>`;
        }).join('');
        return `<table><thead><tr>${headers}</tr></thead><tbody>${rows}</tbody></table>`;
    });

    // Blockquotes
    html = html.replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>');

    // Unordered lists
    html = html.replace(/^[*-] (.+)$/gm, '<li>$1</li>');
    html = html.replace(/((?:<li>.+<\/li>\n?)+)/g, '<ul>$1</ul>');

    // Ordered lists
    html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');

    // Horizontal rule
    html = html.replace(/^---$/gm, '<hr>');

    // Links
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" style="color: var(--accent-cyan);">$1</a>');

    // Paragraphs (lines not already wrapped)
    html = html.replace(/^(?!<[huplitbao]|<\/|<hr)(.+)$/gm, '<p>$1</p>');

    // Clean up empty paragraphs
    html = html.replace(/<p>\s*<\/p>/g, '');

    return html;
}

// ─── UI State ───────────────────────────────────────────────────
function updateUIState(state) {
    const dot = document.getElementById('statusDot');
    const text = document.getElementById('statusText');
    const runBtn = document.getElementById('runBtn');
    const stopBtn = document.getElementById('stopBtn');

    dot.className = 'status-dot';

    switch (state) {
        case 'running':
            dot.classList.add('running');
            text.textContent = 'Agent Working...';
            runBtn.disabled = true;
            runBtn.innerHTML = '<div class="spinner"></div><span>Agent Running...</span>';
            stopBtn.classList.remove('hidden');
            break;
        case 'complete':
            dot.classList.add('complete');
            text.textContent = 'Complete';
            runBtn.disabled = false;
            runBtn.innerHTML = '<span class="btn-icon">🚀</span><span>Launch Agent</span>';
            stopBtn.classList.add('hidden');
            break;
        case 'error':
            dot.classList.add('error');
            text.textContent = 'Error';
            runBtn.disabled = false;
            runBtn.innerHTML = '<span class="btn-icon">🚀</span><span>Launch Agent</span>';
            stopBtn.classList.add('hidden');
            break;
        default:
            text.textContent = 'Ready';
            runBtn.disabled = false;
            runBtn.innerHTML = '<span class="btn-icon">🚀</span><span>Launch Agent</span>';
            stopBtn.classList.add('hidden');
    }
}

// ─── Report Actions ─────────────────────────────────────────────
function copyReport() {
    if (reportContent) {
        navigator.clipboard.writeText(reportContent).then(() => {
            const btn = document.querySelector('.report-actions .btn-icon-only');
            btn.textContent = '✅';
            setTimeout(() => btn.textContent = '📋', 2000);
        });
    }
}

function downloadReport() {
    if (reportContent) {
        const blob = new Blob([reportContent], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'agent-report.md';
        a.click();
        URL.revokeObjectURL(url);
    }
}

// ─── Utilities ──────────────────────────────────────────────────
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ─── Report Modal (Responsive) ──────────────────────────────────
function toggleReportModal() {
    const panel = document.getElementById('reportPanel');
    const overlay = document.getElementById('reportOverlay');
    if (!panel || !overlay) return;
    const isOpen = panel.classList.contains('modal-open');
    panel.classList.toggle('modal-open', !isOpen);
    overlay.classList.toggle('active', !isOpen);
    document.body.style.overflow = isOpen ? '' : 'hidden';
}

function closeReportModal() {
    const panel = document.getElementById('reportPanel');
    const overlay = document.getElementById('reportOverlay');
    if (panel) panel.classList.remove('modal-open');
    if (overlay) overlay.classList.remove('active');
    document.body.style.overflow = '';
}
