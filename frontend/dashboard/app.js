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

// State
let bugs = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupNavigation();
    fetchBugs();
    setupForm();
    
    // Auto refresh every 30 seconds
    setInterval(fetchBugs, 30000);
});

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
        });
    });
}

// API Integration
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
    
    // Re-initialize Lucide icons for new elements
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
                <button class="btn" style="padding: 6px; background: var(--glass-bg);" title="View Details">
                    <i data-lucide="eye" style="width: 16px; height: 16px;"></i>
                </button>
            </td>
        `;
        bugsTableBody.appendChild(row);
    });
}

function updateStats() {
    totalBugsEl.textContent = bugs.length;
    inProgressEl.textContent = bugs.filter(b => b.status === 'processing' || b.status === 'pending').length;
    reproducedEl.textContent = bugs.filter(b => b.status === 'reproduced' || b.status === 'success').length;
    failedEl.textContent = bugs.filter(b => b.status === 'failed' || b.status === 'error').length;
}

function getStatusClass(status) {
    status = status.toLowerCase();
    if (status === 'processing' || status === 'pending') return 'in-progress';
    if (status === 'reproduced' || status === 'success') return 'success';
    if (status === 'failed' || status === 'error') return 'failed';
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
    
    // Basic toast styling injected via JS if not in CSS
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

// Add toast container animation to document
const style = document.createElement('style');
style.textContent = `
    #toast-container {
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        z-index: 1000;
    }
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
`;
document.head.appendChild(style);

refreshBtn.addEventListener('click', fetchBugs);
