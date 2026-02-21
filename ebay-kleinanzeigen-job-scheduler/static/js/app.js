// kleinanzeigen tracker - Main JavaScript

// ============================================================================
// Toast Notification System
// ============================================================================

function showToast(message, type = 'info', duration = 4000) {
    // Create toast container if it doesn't exist
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-width: 400px;
        `;
        document.body.appendChild(container);
    }

    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    // Icon based on type
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    
    toast.innerHTML = `
        <div style="display: flex; align-items: start; gap: 12px;">
            <span style="font-size: 20px; flex-shrink: 0;">${icons[type] || icons.info}</span>
            <div style="flex: 1; padding-top: 2px;">${message}</div>
            <button onclick="this.parentElement.parentElement.remove()" 
                    style="background: none; border: none; color: inherit; cursor: pointer; font-size: 18px; opacity: 0.7; padding: 0; margin: 0; flex-shrink: 0;">
                ✕
            </button>
        </div>
    `;
    
    // Style the toast
    const colors = {
        success: { bg: '#10b981', text: '#ffffff' },
        error: { bg: '#ef4444', text: '#ffffff' },
        warning: { bg: '#f59e0b', text: '#ffffff' },
        info: { bg: '#3b82f6', text: '#ffffff' }
    };
    
    const color = colors[type] || colors.info;
    toast.style.cssText = `
        background: ${color.bg};
        color: ${color.text};
        padding: 16px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        animation: slideInRight 0.3s ease-out;
        min-width: 300px;
        max-width: 100%;
        word-wrap: break-word;
    `;
    
    container.appendChild(toast);
    
    // Auto remove after duration
    if (duration > 0) {
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
}

// Add CSS animations for toasts
if (!document.getElementById('toast-styles')) {
    const style = document.createElement('style');
    style.id = 'toast-styles';
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
        
        .confirm-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10001;
            animation: fadeIn 0.2s ease-out;
        }
        
        .confirm-dialog {
            background: var(--card-bg);
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            max-width: 400px;
            width: 90%;
            padding: 24px;
            animation: scaleIn 0.2s ease-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes scaleIn {
            from { transform: scale(0.9); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }
    `;
    document.head.appendChild(style);
}

// Custom confirm dialog
function showConfirm(message, onConfirm, onCancel) {
    // Create overlay
    const overlay = document.createElement('div');
    overlay.className = 'confirm-overlay';
    
    // Create dialog
    const dialog = document.createElement('div');
    dialog.className = 'confirm-dialog';
    
    // Explicit styling for better visibility
    dialog.style.cssText = `
        background: #ffffff;
        color: #1f2937;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        max-width: 400px;
        width: 90%;
        padding: 24px;
        animation: scaleIn 0.2s ease-out;
    `;
    
    // Check if dark mode
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    if (isDark) {
        dialog.style.background = '#1f2937';
        dialog.style.color = '#f3f4f6';
    }
    
    dialog.innerHTML = `
        <div style="margin-bottom: 20px; font-size: 16px; line-height: 1.5; font-weight: 500;">
            ${message}
        </div>
        <div style="display: flex; gap: 12px; justify-content: flex-end;">
            <button id="confirmCancel" 
                    style="padding: 10px 20px; border: 1px solid #d1d5db; background: #f3f4f6; color: #374151; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 500;">
                Cancel
            </button>
            <button id="confirmOk" 
                    style="padding: 10px 20px; border: none; background: #dc2626; color: #ffffff; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 500;">
                Confirm
            </button>
        </div>
    `;
    
    overlay.appendChild(dialog);
    document.body.appendChild(overlay);
    
    // Focus on confirm button
    setTimeout(() => document.getElementById('confirmOk').focus(), 100);
    
    // Handle confirm
    document.getElementById('confirmOk').onclick = () => {
        overlay.remove();
        if (onConfirm) onConfirm();
    };
    
    // Handle cancel
    document.getElementById('confirmCancel').onclick = () => {
        overlay.remove();
        if (onCancel) onCancel();
    };
    
    // Handle ESC key
    const handleEsc = (e) => {
        if (e.key === 'Escape') {
            overlay.remove();
            if (onCancel) onCancel();
            document.removeEventListener('keydown', handleEsc);
        }
    };
    document.addEventListener('keydown', handleEsc);
    
    // Handle click outside
    overlay.onclick = (e) => {
        if (e.target === overlay) {
            overlay.remove();
            if (onCancel) onCancel();
        }
    };
    
    // Prevent click inside dialog from closing
    dialog.onclick = (e) => e.stopPropagation();
}

// Internationalization (i18n)
const translations = {
    en: {
        appTitle: '<img src="/static/logo.svg" alt="logo" style="height: 1.5em; vertical-align: middle; margin-right: 0.4em;">kleinanzeigen tracker',
        logout: 'Logout',
        welcomeBack: '🔐 Welcome Back',
        signInDesc: 'Sign in to manage your kleinanzeigen jobs',
        username: 'Username',
        password: 'Password',
        signIn: 'Sign In',
        jobs: 'Jobs',
        configuration: 'Configuration',
        health: 'Health',
        totalJobs: 'Total Jobs',
        activeJobs: 'Active Jobs',
        successRate: 'Success Rate',
        scheduledJobs: 'Scheduled Jobs',
        createJob: '+ Create Job',
        name: 'Name',
        url: 'URL',
        schedule: 'Schedule',
        status: 'Status',
        lastRun: 'Last Run',
        actions: 'Actions',
        noJobsYet: 'No jobs yet',
        noJobsDesc: 'Create your first job to start monitoring kleinanzeigen.de',
        createNewJob: 'Create New Job',
        editJob: 'Edit Job',
        updateJob: 'Update Job',
        jobName: 'Job Name',
        searchUrlPath: 'Search URL Path',
        urlPlaceholder: 'Example: /s-wohnzimmer/tisch/k0c88',
        scheduleLabel: 'Schedule',
        enableJob: 'Enable job immediately',
        cancel: 'Cancel',
        runNow: '▶ Run Now',
        delete: 'Delete',
        enabled: 'Enabled',
        disabled: 'Disabled',
        success: '✓ Success',
        failed: '✗ Failed',
        never: 'Never',
        systemConfig: 'System Configuration',
        saveChanges: 'Save Changes',
        serviceHealth: 'Service Health',
        refresh: '🔄 Refresh',
        healthy: '✓ Healthy',
        error: '✗ Error',
        selectPreset: '-- Select a preset or use custom --',
        commonIntervals: 'Common Intervals',
        every5min: 'Every 5 minutes',
        every10min: 'Every 10 minutes',
        every15min: 'Every 15 minutes',
        every30min: 'Every 30 minutes',
        everyHour: 'Every hour',
        every2hours: 'Every 2 hours',
        every6hours: 'Every 6 hours',
        every12hours: 'Every 12 hours',
        daily: 'Daily',
        dailyAt8am: 'Daily at 8:00 AM',
        dailyAt12pm: 'Daily at 12:00 PM',
        dailyAt6pm: 'Daily at 6:00 PM',
        dailyAt8pm: 'Daily at 8:00 PM',
        dailyAtMidnight: 'Daily at midnight',
        weekdays: 'Weekdays',
        weekdaysAt9am: 'Weekdays at 9:00 AM',
        weekdaysAt6pm: 'Weekdays at 6:00 PM',
        weekend: 'Weekend',
        weekendAt10am: 'Weekend at 10:00 AM',
        customCron: 'Custom cron expression...',
        addAnotherUrl: '+ Add Another URL',
        urlPathsHelp: 'Add multiple URLs to monitor several searches in one job. Results will be combined and deduplicated.',
        urlPathExample: 'Example: From https://www.kleinanzeigen.de/s-wohnzimmer/tisch/k0c88 use only <code>/s-wohnzimmer/tisch/k0c88</code>',
        cronFormatHelp: 'Format: minute hour day month weekday',
        cronExample: 'Example: */30 * * * * = every 30 minutes',
        useCrontabGuru: 'Use crontab.guru for help',
        jobsEnabledNote: 'ℹ️ Note: Jobs are created as enabled by default. Use the "✓ Enabled / ✗ Disabled" button in the jobs table to enable/disable jobs (including notifications).',
        changePassword: 'Change Password',
        currentPassword: 'Current Password',
        newPassword: 'New Password',
        confirmNewPassword: 'Confirm New Password',
        requirements: 'Requirements:',
        minChars: 'Minimum 6 characters',
        mustContain: 'Must contain at least one number or special character',
        mustDiffer: 'Must be different from current password',
        passwordChangeNote: '⚠️ Note: After changing your password, you will be logged out and need to sign in again with your new password.',
        passwordChanged: 'Password changed successfully! Redirecting to login...',
        priorityLabel: '🔔 Priority Job',
        priorityDesc: 'When enabled, notifications for this job will include <strong>@everyone</strong> at the end of the title to alert all channel members.'
    },
    de: {
        appTitle: '<img src="/static/logo.svg" alt="logo" style="height: 1.5em; vertical-align: middle; margin-right: 0.4em;">kleinanzeigen tracker',
        logout: 'Abmelden',
        welcomeBack: '🔐 Willkommen zurück',
        signInDesc: 'Melden Sie sich an, um Ihre Kleinanzeigen-Jobs zu verwalten',
        username: 'Benutzername',
        password: 'Passwort',
        signIn: 'Anmelden',
        jobs: 'Jobs',
        configuration: 'Konfiguration',
        health: 'Status',
        totalJobs: 'Jobs gesamt',
        activeJobs: 'Aktive Jobs',
        successRate: 'Erfolgsrate',
        scheduledJobs: 'Geplante Jobs',
        createJob: '+ Job erstellen',
        name: 'Name',
        url: 'URL',
        schedule: 'Zeitplan',
        status: 'Status',
        lastRun: 'Letzte Ausführung',
        actions: 'Aktionen',
        noJobsYet: 'Noch keine Jobs',
        noJobsDesc: 'Erstellen Sie Ihren ersten Job, um kleinanzeigen.de zu überwachen',
        createNewJob: 'Neuen Job erstellen',
        editJob: 'Job bearbeiten',
        updateJob: 'Job aktualisieren',
        jobName: 'Job-Name',
        searchUrlPath: 'Such-URL-Pfad',
        urlPlaceholder: 'Beispiel: /s-wohnzimmer/tisch/k0c88',
        scheduleLabel: 'Zeitplan',
        enableJob: 'Job sofort aktivieren',
        cancel: 'Abbrechen',
        runNow: '▶ Jetzt starten',
        delete: 'Löschen',
        enabled: 'Aktiviert',
        disabled: 'Deaktiviert',
        success: '✓ Erfolg',
        failed: '✗ Fehler',
        never: 'Nie',
        systemConfig: 'Systemkonfiguration',
        saveChanges: 'Änderungen speichern',
        serviceHealth: 'Service-Status',
        refresh: '🔄 Aktualisieren',
        healthy: '✓ Gesund',
        error: '✗ Fehler',
        selectPreset: '-- Voreinstellung wählen oder benutzerdefiniert --',
        commonIntervals: 'Häufige Intervalle',
        every5min: 'Alle 5 Minuten',
        every10min: 'Alle 10 Minuten',
        every15min: 'Alle 15 Minuten',
        every30min: 'Alle 30 Minuten',
        everyHour: 'Jede Stunde',
        every2hours: 'Alle 2 Stunden',
        every6hours: 'Alle 6 Stunden',
        every12hours: 'Alle 12 Stunden',
        daily: 'Täglich',
        dailyAt8am: 'Täglich um 8:00 Uhr',
        dailyAt12pm: 'Täglich um 12:00 Uhr',
        dailyAt6pm: 'Täglich um 18:00 Uhr',
        dailyAt8pm: 'Täglich um 20:00 Uhr',
        dailyAtMidnight: 'Täglich um Mitternacht',
        weekdays: 'Wochentage',
        weekdaysAt9am: 'Wochentags um 9:00 Uhr',
        weekdaysAt6pm: 'Wochentags um 18:00 Uhr',
        weekend: 'Wochenende',
        weekendAt10am: 'Am Wochenende um 10:00 Uhr',
        customCron: 'Benutzerdefinierter Cron-Ausdruck...',
        addAnotherUrl: '+ Weitere URL hinzufügen',
        urlPathsHelp: 'Fügen Sie mehrere URLs hinzu, um verschiedene Suchen in einem Job zu überwachen. Ergebnisse werden kombiniert und dedupliziert.',
        urlPathExample: 'Beispiel: Von https://www.kleinanzeigen.de/s-wohnzimmer/tisch/k0c88 nur <code>/s-wohnzimmer/tisch/k0c88</code> verwenden',
        cronFormatHelp: 'Format: Minute Stunde Tag Monat Wochentag',
        cronExample: 'Beispiel: */30 * * * * = alle 30 Minuten',
        useCrontabGuru: 'Nutzen Sie crontab.guru für Hilfe',
        jobsEnabledNote: 'ℹ️ Hinweis: Jobs werden standardmäßig als aktiviert erstellt. Verwenden Sie die Schaltfläche "✓ Aktiviert / ✗ Deaktiviert" in der Jobtabelle, um Jobs zu aktivieren/deaktivieren (einschließlich Benachrichtigungen).',
        changePassword: 'Passwort ändern',
        currentPassword: 'Aktuelles Passwort',
        newPassword: 'Neues Passwort',
        confirmNewPassword: 'Neues Passwort bestätigen',
        requirements: 'Anforderungen:',
        minChars: 'Mindestens 6 Zeichen',
        mustContain: 'Muss mindestens eine Zahl oder ein Sonderzeichen enthalten',
        mustDiffer: 'Muss sich vom aktuellen Passwort unterscheiden',
        passwordChangeNote: '⚠️ Hinweis: Nach der Änderung Ihres Passworts werden Sie abgemeldet und müssen sich mit Ihrem neuen Passwort erneut anmelden.',
        passwordChanged: 'Passwort erfolgreich geändert! Weiterleitung zur Anmeldung...',
        priorityLabel: '🔔 Prioritäts-Job',
        priorityDesc: 'Wenn aktiviert, enthalten Benachrichtigungen für diesen Job <strong>@everyone</strong> am Ende des Titels, um alle Kanalmitglieder zu benachrichtigen.'
    }
};

// Detect browser language
let currentLanguage = (navigator.language || navigator.userLanguage).split('-')[0];
if (!translations[currentLanguage]) {
    currentLanguage = 'en'; // Fallback to English
}

// Apply translations
function applyTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[currentLanguage][key]) {
            // Handle optgroup labels
            if (element.tagName === 'OPTGROUP') {
                element.setAttribute('label', translations[currentLanguage][key]);
            }
            // Handle buttons and inputs
            else if (element.tagName === 'INPUT' || element.tagName === 'BUTTON') {
                if (element.type === 'button' || element.type === 'submit') {
                    element.textContent = translations[currentLanguage][key];
                }
            }
            // Handle option elements - set both text content and keep value
            else if (element.tagName === 'OPTION') {
                element.textContent = translations[currentLanguage][key];
            }
            // Special handling for appTitle to allow HTML (logo image)
            else if (key === 'appTitle') {
                element.innerHTML = translations[currentLanguage][key];
            }
            // Handle all other elements
            else {
                element.textContent = translations[currentLanguage][key];
            }
        }
    });
}

// Theme Management
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const icon = document.getElementById('themeIcon');
    if (icon) {
        icon.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
}

// API Configuration
const API_BASE = window.location.origin;
let accessToken = localStorage.getItem('accessToken');
let refreshToken = localStorage.getItem('refreshToken');
let currentUser = null;

// Store current editing job ID
let editingJobId = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    applyTranslations();
    
    if (accessToken) {
        validateToken();
    } else {
        showLogin();
    }

    // Setup event listeners
    setupEventListeners();
});

function setupEventListeners() {
    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    // Job form
    const jobForm = document.getElementById('jobForm');
    if (jobForm) {
        jobForm.addEventListener('submit', handleJobSubmit);
    }

    // Password change form
    const changePasswordForm = document.getElementById('changePasswordForm');
    if (changePasswordForm) {
        changePasswordForm.addEventListener('submit', handleChangePassword);
    }

    // Custom schedule input listener
    const jobScheduleInput = document.getElementById('jobSchedule');
    if (jobScheduleInput) {
        jobScheduleInput.addEventListener('input', (e) => {
            updateScheduleDescription(e.target.value);
        });
    }
}

// Authentication
async function validateToken() {
    try {
        const response = await apiCall('/api/auth/me', 'GET');
        currentUser = response.user;
        showApp();
    } catch (error) {
        if (refreshToken) {
            try {
                await refreshAccessToken();
                validateToken();
            } catch (e) {
                showLogin();
            }
        } else {
            showLogin();
        }
    }
}

async function refreshAccessToken() {
    const response = await fetch(`${API_BASE}/api/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken })
    });

    if (!response.ok) throw new Error('Refresh failed');

    const data = await response.json();
    accessToken = data.access_token;
    refreshToken = data.refresh_token;
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
}

async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    document.getElementById('loginBtnText').style.display = 'none';
    document.getElementById('loginSpinner').style.display = 'block';
    document.getElementById('loginError').style.display = 'none';

    try {
        const response = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            accessToken = data.access_token;
            refreshToken = data.refresh_token;
            currentUser = data.user;
            localStorage.setItem('accessToken', accessToken);
            localStorage.setItem('refreshToken', refreshToken);
            showApp();
        } else {
            document.getElementById('loginError').textContent = data.error || 'Login failed';
            document.getElementById('loginError').style.display = 'block';
        }
    } catch (error) {
        document.getElementById('loginError').textContent = 'Network error. Please try again.';
        document.getElementById('loginError').style.display = 'block';
    } finally {
        document.getElementById('loginBtnText').style.display = 'block';
        document.getElementById('loginSpinner').style.display = 'none';
    }
}

function logout() {
    accessToken = null;
    refreshToken = null;
    currentUser = null;
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    showLogin();
}

function showLogin() {
    document.getElementById('loginPage').style.display = 'flex';
    document.getElementById('appContainer').style.display = 'none';
}

function showApp() {
    document.getElementById('loginPage').style.display = 'none';
    document.getElementById('appContainer').style.display = 'block';
    document.getElementById('currentUser').textContent = currentUser.username;
    loadJobs();
    loadConfig();
}

// API Helper
async function apiCall(endpoint, method = 'GET', body = null) {
    const options = {
        method,
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        }
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    const response = await fetch(`${API_BASE}${endpoint}`, options);

    // Don't try to refresh token for password change endpoint (401 means wrong password)
    if (response.status === 401 && endpoint !== '/api/auth/change-password') {
        if (refreshToken) {
            await refreshAccessToken();
            return apiCall(endpoint, method, body);
        } else {
            logout();
            throw new Error('Unauthorized');
        }
    }

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'API Error');
    }

    return data;
}

// Tab switching
function switchTab(tabName) {
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    event.target.classList.add('active');

    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    document.getElementById(`${tabName}Tab`).classList.add('active');

    if (tabName === 'jobs') loadJobs();
    if (tabName === 'config') loadConfig();
    if (tabName === 'health') loadHealth();
}

// Jobs Management
async function loadJobs() {
    document.getElementById('jobsLoading').style.display = 'flex';
    document.getElementById('jobsTable').style.display = 'none';
    document.getElementById('jobsEmpty').style.display = 'none';

    try {
        const data = await apiCall('/api/jobs');
        const jobs = data.jobs;

        if (jobs.length === 0) {
            document.getElementById('jobsEmpty').style.display = 'block';
        } else {
            renderJobs(jobs);
            document.getElementById('jobsTable').style.display = 'block';
        }

        updateStats(jobs);
    } catch (error) {
        console.error('Failed to load jobs:', error);
    } finally {
        document.getElementById('jobsLoading').style.display = 'none';
    }
}

function renderJobs(jobs) {
    const tbody = document.getElementById('jobsTableBody');
    const t = translations[currentLanguage];
    
    tbody.innerHTML = jobs.map(job => {
        const readableSchedule = cronToReadable(job.schedule);
        const cleanSchedule = readableSchedule.replace(/<[^>]*>/g, '').replace('Will run ', '');
        
        return `
        <tr>
            <td><strong>${job.name}</strong></td>
            <td>${formatUrlsForDisplay(job.url)}</td>
            <td>
                <div style="font-size: 13px;">${cleanSchedule}</div>
                <small style="color: var(--text-secondary); font-size: 11px;">
                    <code>${job.schedule}</code>
                </small>
            </td>
            <td>
                ${job.enabled 
                    ? `<span class="badge badge-success">${t.enabled}</span>` 
                    : `<span class="badge badge-danger">${t.disabled}</span>`}
                ${job.last_status === 'success' 
                    ? `<span class="badge badge-success">${t.success}</span>` 
                    : job.last_status === 'failed' 
                    ? `<span class="badge badge-danger">${t.failed}</span>` 
                    : ''}
            </td>
            <td>${job.last_run ? new Date(job.last_run).toLocaleString() : t.never}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="runJobNow(${job.id})" title="Run job now">▶ Run</button>
                <button class="btn btn-sm ${job.enabled ? 'btn-success' : 'btn-secondary'}" 
                        onclick="toggleJob(${job.id}, ${job.enabled ? 'false' : 'true'})" 
                        title="${job.enabled ? 'Disable job (stops execution and notifications)' : 'Enable job (starts execution and notifications)'}">
                    ${job.enabled ? '✓ Enabled' : '✗ Disabled'}
                </button>
                <button class="btn btn-sm ${job.priority ? 'btn-priority' : 'btn-secondary'}"
                        onclick="togglePriority(${job.id}, ${job.priority ? 'false' : 'true'})"
                        title="${job.priority ? 'Disable priority (@everyone)' : 'Enable priority (@everyone)'}">
                    ${job.priority ? '🔔 Priority' : '🔕 Priority'}
                </button>
                <button class="btn btn-sm btn-secondary" onclick="editJob(${job.id})" title="Edit job">✏️ Edit</button>
                <button class="btn btn-sm btn-danger" onclick="deleteJob(${job.id}, '${job.name}')" title="Delete job">🗑️ Delete</button>
            </td>
        </tr>
    `}).join('');
}

function updateStats(jobs) {
    document.getElementById('totalJobs').textContent = jobs.length;
    document.getElementById('activeJobs').textContent = jobs.filter(j => j.enabled).length;
    
    const successJobs = jobs.filter(j => j.last_status === 'success').length;
    const rate = jobs.length > 0 ? Math.round((successJobs / jobs.length) * 100) : 0;
    document.getElementById('successRate').textContent = rate + '%';
}

// Schedule Helper Functions
function updateScheduleFromPreset() {
    const preset = document.getElementById('schedulePreset').value;
    const customGroup = document.getElementById('customScheduleGroup');
    const scheduleInput = document.getElementById('jobSchedule');
    
    if (preset === 'custom') {
        customGroup.style.display = 'block';
        updateScheduleDescription(scheduleInput.value);
    } else if (preset) {
        customGroup.style.display = 'none';
        scheduleInput.value = preset;
        updateScheduleDescription(preset);
    } else {
        customGroup.style.display = 'none';
        scheduleInput.value = '*/30 * * * *';
        updateScheduleDescription('*/30 * * * *');
    }
}

function updateScheduleDescription(cronExpr) {
    const description = document.getElementById('scheduleText');
    const readable = cronToReadable(cronExpr);
    description.innerHTML = readable;
}

function cronToReadable(cron) {
    const lang = currentLanguage === 'de' ? 'de' : 'en';
    const descriptions = {
        en: {
            '*/5 * * * *': 'Will run every 5 minutes',
            '*/10 * * * *': 'Will run every 10 minutes',
            '*/15 * * * *': 'Will run every 15 minutes',
            '*/30 * * * *': 'Will run every 30 minutes',
            '0 * * * *': 'Will run every hour',
            '0 */2 * * *': 'Will run every 2 hours',
            '0 */6 * * *': 'Will run every 6 hours',
            '0 */12 * * *': 'Will run every 12 hours',
            '0 8 * * *': 'Will run daily at 8:00 AM',
            '0 12 * * *': 'Will run daily at 12:00 PM',
            '0 18 * * *': 'Will run daily at 6:00 PM',
            '0 20 * * *': 'Will run daily at 8:00 PM',
            '0 0 * * *': 'Will run daily at midnight',
            '0 9 * * 1-5': 'Will run weekdays at 9:00 AM',
            '0 18 * * 1-5': 'Will run weekdays at 6:00 PM',
            '0 10 * * 0,6': 'Will run weekends at 10:00 AM'
        },
        de: {
            '*/5 * * * *': 'Wird alle 5 Minuten ausgeführt',
            '*/10 * * * *': 'Wird alle 10 Minuten ausgeführt',
            '*/15 * * * *': 'Wird alle 15 Minuten ausgeführt',
            '*/30 * * * *': 'Wird alle 30 Minuten ausgeführt',
            '0 * * * *': 'Wird jede Stunde ausgeführt',
            '0 */2 * * *': 'Wird alle 2 Stunden ausgeführt',
            '0 */6 * * *': 'Wird alle 6 Stunden ausgeführt',
            '0 */12 * * *': 'Wird alle 12 Stunden ausgeführt',
            '0 8 * * *': 'Wird täglich um 8:00 Uhr ausgeführt',
            '0 12 * * *': 'Wird täglich um 12:00 Uhr ausgeführt',
            '0 18 * * *': 'Wird täglich um 18:00 Uhr ausgeführt',
            '0 20 * * *': 'Wird täglich um 20:00 Uhr ausgeführt',
            '0 0 * * *': 'Wird täglich um Mitternacht ausgeführt',
            '0 9 * * 1-5': 'Wird wochentags um 9:00 Uhr ausgeführt',
            '0 18 * * 1-5': 'Wird wochentags um 18:00 Uhr ausgeführt',
            '0 10 * * 0,6': 'Wird am Wochenende um 10:00 Uhr ausgeführt'
        }
    };
    
    return descriptions[lang][cron] || `Custom: ${cron} (<a href="https://crontab.guru/#${encodeURIComponent(cron)}" target="_blank" style="color: var(--primary);">crontab.guru</a>)`;
}

async function showCreateJobModal() {
    const t = translations[currentLanguage];
    
    document.getElementById('jobModalTitle').textContent = t.createNewJob;
    document.getElementById('jobForm').reset();
    document.getElementById('jobFormBtnText').textContent = t.createJob || 'Create Job';

    // Update dynamic text elements
    document.getElementById('addUrlButton').textContent = t.addAnotherUrl;
    document.getElementById('urlPathsHelpText').textContent = t.urlPathsHelp;
    document.getElementById('urlPathExample').innerHTML = t.urlPathExample;
    document.getElementById('jobsEnabledNote').innerHTML = t.jobsEnabledNote;

    // Update priority toggle text
    document.getElementById('priorityLabel').textContent = t.priorityLabel;
    document.getElementById('priorityDesc').innerHTML = t.priorityDesc;
    document.getElementById('jobPriority').checked = false;

    // Initialize URL fields with one empty field
    setUrlsToFields('');

    // Load default schedule from config
    let defaultSchedule = '*/30 * * * *'; // Fallback default
    try {
        const configData = await apiCall('/api/config');
        if (configData.config && configData.config.default_job_schedule) {
            defaultSchedule = configData.config.default_job_schedule.value;
        }
    } catch (error) {
        console.warn('Failed to load default schedule from config, using fallback:', error);
    }

    // Set the default schedule
    document.getElementById('schedulePreset').value = defaultSchedule;
    document.getElementById('customScheduleGroup').style.display = 'none';
    document.getElementById('jobSchedule').value = defaultSchedule;
    updateScheduleDescription(defaultSchedule);

    document.getElementById('jobModal').classList.add('active');
}

function closeJobModal() {
    document.getElementById('jobModal').classList.remove('active');
    editingJobId = null; // Reset editing mode
}

async function handleJobSubmit(e) {
    e.preventDefault();

    const jobData = {
        name: document.getElementById('jobName').value,
        url: getUrlsFromFields(),  // Get comma-separated URLs from fields
        schedule: document.getElementById('jobSchedule').value,
        enabled: true,  // Always create jobs as enabled
        notify_enabled: true,  // Always enable notifications (controlled by enabled/disabled button)
        priority: document.getElementById('jobPriority').checked
    };

    document.getElementById('jobFormBtnText').style.display = 'none';
    document.getElementById('jobFormSpinner').style.display = 'block';

    try {
        if (editingJobId) {
            // Update existing job
            await apiCall(`/api/jobs/${editingJobId}`, 'PUT', jobData);
        } else {
            // Create new job
            await apiCall('/api/jobs', 'POST', jobData);
        }
        closeJobModal();
        loadJobs();
        showToast(editingJobId ? 'Job updated successfully!' : 'Job created successfully!', 'success');
    } catch (error) {
        showToast('Error ' + (editingJobId ? 'updating' : 'creating') + ' job: ' + error.message, 'error');
    } finally {
        document.getElementById('jobFormBtnText').style.display = 'block';
        document.getElementById('jobFormSpinner').style.display = 'none';
    }
}

async function editJob(jobId) {
    try {
        const data = await apiCall(`/api/jobs/${jobId}`);
        const job = data.job;
        
        // Set editing mode
        editingJobId = jobId;
        const t = translations[currentLanguage];
        document.getElementById('jobModalTitle').textContent = t.editJob + ': ' + job.name;
        document.getElementById('jobFormBtnText').textContent = t.updateJob;
        
        // Update dynamic text elements (same as showCreateJobModal for consistency)
        document.getElementById('addUrlButton').textContent = t.addAnotherUrl;
        document.getElementById('urlPathsHelpText').textContent = t.urlPathsHelp;
        document.getElementById('urlPathExample').innerHTML = t.urlPathExample;
        document.getElementById('jobsEnabledNote').innerHTML = t.jobsEnabledNote;

        // Update priority toggle text
        document.getElementById('priorityLabel').textContent = t.priorityLabel;
        document.getElementById('priorityDesc').innerHTML = t.priorityDesc;

        // Populate form fields
        document.getElementById('jobName').value = job.name;
        setUrlsToFields(job.url);  // Populate URL fields with comma-separated URLs
        document.getElementById('jobSchedule').value = job.schedule;
        
        // Set schedule preset if it matches
        const preset = document.getElementById('schedulePreset');
        let matchedPreset = false;
        for (let i = 0; i < preset.options.length; i++) {
            if (preset.options[i].value === job.schedule) {
                preset.value = job.schedule;
                matchedPreset = true;
                break;
            }
        }
        if (!matchedPreset) {
            preset.value = 'custom';
            document.getElementById('customScheduleGroup').style.display = 'block';
        }
        
        updateScheduleDescription(job.schedule);

        // Populate priority checkbox
        document.getElementById('jobPriority').checked = !!job.priority;

        // Show modal
        document.getElementById('jobModal').classList.add('active');
    } catch (error) {
        showToast('Error loading job: ' + error.message, 'error');
    }
}

async function runJobNow(jobId) {
    const t = translations[currentLanguage];
    
    showConfirm(t.runNow + '?', async () => {
        try {
            await apiCall(`/api/jobs/${jobId}/run`, 'POST');
            showToast('Job execution started!', 'success');
            setTimeout(loadJobs, 2000);
        } catch (error) {
            showToast('Error: ' + error.message, 'error');
        }
    });
}

async function togglePriority(jobId, newState) {
    try {
        const priority = newState === 'true' || newState === true;
        await apiCall(`/api/jobs/${jobId}`, 'PUT', { priority: priority });
        loadJobs();
        showToast('Job priority ' + (priority ? 'enabled' : 'disabled') + '!', 'success');
    } catch (error) {
        showToast('Error updating priority: ' + error.message, 'error');
    }
}

async function toggleJob(jobId, newState) {
    try {
        const enabled = newState === 'true' || newState === true;
        await apiCall(`/api/jobs/${jobId}`, 'PUT', {
            enabled: enabled,
            notify_enabled: enabled  // Both fields follow the same state
        });
        loadJobs(); // Reload to show updated state
        showToast('Job ' + (enabled ? 'enabled' : 'disabled') + ' successfully!', 'success');
    } catch (error) {
        showToast('Error toggling job: ' + error.message, 'error');
    }
}

async function deleteJob(jobId, jobName) {
    const t = translations[currentLanguage];
    
    showConfirm(`${t.delete} "${jobName}"?`, async () => {
        try {
            await apiCall(`/api/jobs/${jobId}`, 'DELETE');
            loadJobs();
            showToast('Job deleted successfully!', 'success');
        } catch (error) {
            showToast('Error: ' + error.message, 'error');
        }
    });
}

// Configuration
async function loadConfig() {
    try {
        const data = await apiCall('/api/config');
        renderConfig(data.config);
    } catch (error) {
        console.error('Failed to load config:', error);
    }
}

function renderConfig(config) {
    const form = document.getElementById('configForm');
    const t = translations[currentLanguage];
    const lang = currentLanguage;

    // ── helper: build a single field ──────────────────────────────────────
    function fieldHtml(key, value, description) {
        if (key === 'notification_language') {
            return `
                <div class="form-group">
                    <label for="config-${key}">${key.replace(/_/g, ' ').toUpperCase()}</label>
                    <select id="config-${key}" data-key="${key}">
                        <option value="de" ${value === 'de' ? 'selected' : ''}>🇩🇪 Deutsch (German)</option>
                        <option value="en" ${value === 'en' ? 'selected' : ''}>🇬🇧 English</option>
                    </select>
                    <small style="color:var(--text-secondary);">${description}</small>
                </div>`;
        }
        if (key === 'default_job_schedule') {
            const cronReadable = cronToReadable(value);
            const cronHelp = lang === 'de'
                ? `Cron-Format: Minute Stunde Tag Monat Wochentag<br>Beispiel: */30 * * * * = alle 30 Minuten | 0 8 * * * = täglich um 8:00 Uhr<br><a href="https://crontab.guru/" target="_blank" style="color:var(--primary);">crontab.guru</a>`
                : `Cron format: minute hour day month weekday<br>Example: */30 * * * * = every 30 minutes | 0 8 * * * = daily at 8:00 AM<br><a href="https://crontab.guru/" target="_blank" style="color:var(--primary);">crontab.guru</a>`;
            return `
                <div class="form-group">
                    <label for="config-${key}">${key.replace(/_/g, ' ').toUpperCase()}</label>
                    <input type="text" id="config-${key}" value="${value}" data-key="${key}" oninput="updateConfigScheduleDescription(this.value)">
                    <div id="configScheduleDescription" style="padding:10px;background:var(--bg);border-radius:6px;margin-top:8px;font-size:13px;color:var(--text-secondary);">
                        <strong>⏰ Schedule:</strong> <span id="configScheduleText">${cronReadable}</span>
                    </div>
                    <small style="color:var(--text-secondary);display:block;margin-top:4px;">${cronHelp}</small>
                </div>`;
        }
        return `
            <div class="form-group">
                <label for="config-${key}">${key.replace(/_/g, ' ').toUpperCase()}</label>
                <input type="text" id="config-${key}" value="${value}" data-key="${key}">
                <small style="color:var(--text-secondary);">${description}</small>
            </div>`;
    }

    // ── descriptions ──────────────────────────────────────────────────────
    const desc = {
        en: {
            scraper_api_url:        'Ebay Kleinanzeigen Scraper API base URL',
            scraper_api_key:        'API key for authenticating with the Scraper API',
            scraper_request_timeout:'Request timeout in seconds when calling the Scraper API',
            notification_language:  'Language for notification messages: "de" (German) or "en" (English)',
            default_job_schedule:   'Default cron schedule for new jobs',
            matterbridge_url:       'Matterbridge API base URL (e.g. http://matterbridge:4242)',
            matterbridge_token:     'Bearer token for Matterbridge API authentication',
            matterbridge_gateway:   'Matterbridge gateway name to send messages through',
            matterbridge_username:  'Username displayed in Matterbridge messages',
            apprise_api_url:        'Apprise API container base URL (e.g. http://apprise:8000)',
            apprise_api_key:        'Apprise notification key/ID (e.g. kleinanzeigen) — messages are sent to POST /notify/{key}',
            apprise_username:       'Optional: HTTP Basic Auth username — only needed if Apprise is behind a reverse proxy with authentication enabled',
            apprise_password:       'Optional: HTTP Basic Auth password — only needed if Apprise is behind a reverse proxy with authentication enabled',
        },
        de: {
            scraper_api_url:        'Ebay Kleinanzeigen Scraper API Basis-URL',
            scraper_api_key:        'API-Schlüssel zur Authentifizierung mit der Scraper-API',
            scraper_request_timeout:'Anfrage-Timeout in Sekunden beim Aufruf der Scraper-API',
            notification_language:  'Sprache für Benachrichtigungsmeldungen: "de" (Deutsch) oder "en" (Englisch)',
            default_job_schedule:   'Standard-Cron-Zeitplan für neue Jobs',
            matterbridge_url:       'Matterbridge API Basis-URL (z.B. http://matterbridge:4242)',
            matterbridge_token:     'Bearer-Token für Matterbridge API Authentifizierung',
            matterbridge_gateway:   'Matterbridge Gateway-Name zum Senden von Nachrichten',
            matterbridge_username:  'Benutzername, der in Matterbridge-Nachrichten angezeigt wird',
            apprise_api_url:        'Apprise API Container Basis-URL (z.B. http://apprise:8000)',
            apprise_api_key:        'Apprise Benachrichtigungsschlüssel (z.B. kleinanzeigen) — Nachrichten werden an POST /notify/{key} gesendet',
            apprise_username:       'Optional: HTTP Basic Auth Benutzername — nur nötig, wenn Apprise hinter einem Reverse Proxy mit Authentifizierung betrieben wird',
            apprise_password:       'Optional: HTTP Basic Auth Passwort — nur nötig, wenn Apprise hinter einem Reverse Proxy mit Authentifizierung betrieben wird',
        }
    };

    const d = desc[lang] || desc.en;

    // ── section labels ─────────────────────────────────────────────────────
    const labels = {
        en: {
            scraper:        '🔍 Scraper API',
            general:        '⚙️ General Settings',
            matterbridge:   '💬 Matterbridge',
            matterbridgeDesc: 'Connect to a Matterbridge instance to forward notifications to chat platforms (Matrix, Slack, Discord, …)',
            apprise:        '🔔 Apprise',
            appriseDesc:    'Connect to an Apprise API container to send notifications to 80+ services (Telegram, Discord, Pushover, ntfy, Signal, …)',
        },
        de: {
            scraper:        '🔍 Scraper API',
            general:        '⚙️ Allgemeine Einstellungen',
            matterbridge:   '💬 Matterbridge',
            matterbridgeDesc: 'Mit einer Matterbridge-Instanz verbinden, um Benachrichtigungen an Chat-Plattformen weiterzuleiten (Matrix, Slack, Discord, …)',
            apprise:        '🔔 Apprise',
            appriseDesc:    'Mit einem Apprise API-Container verbinden, um Benachrichtigungen an 80+ Dienste zu senden (Telegram, Discord, Pushover, ntfy, Signal, …)',
        }
    };
    const l = labels[lang] || labels.en;

    // Read enabled flags from saved config
    const matterbridgeEnabled = config.matterbridge_enabled?.value === 'true';
    const appriseEnabled = config.apprise_enabled?.value === 'true';

    form.innerHTML = `
        <style>
            .notification-section {
                border: 1px solid var(--border);
                border-radius: 10px;
                padding: 16px;
                margin-bottom: 4px;
            }
            .notification-section-fields {
                margin-top: 16px;
                padding-top: 16px;
                border-top: 1px solid var(--border);
                animation: fadeInDown .2s ease-out;
            }
            @keyframes fadeInDown {
                from { opacity: 0; transform: translateY(-8px); }
                to   { opacity: 1; transform: translateY(0); }
            }
        </style>

        <!-- ── Scraper API ── -->
        <div class="config-section">
            <h3 style="margin-bottom:12px;font-size:15px;">${l.scraper}</h3>
            ${fieldHtml('scraper_api_url',         config.scraper_api_url?.value         || '', d.scraper_api_url)}
            ${fieldHtml('scraper_api_key',         config.scraper_api_key?.value         || '', d.scraper_api_key)}
            ${fieldHtml('scraper_request_timeout', config.scraper_request_timeout?.value || '', d.scraper_request_timeout)}
        </div>

        <hr style="border:none;border-top:1px solid var(--border);margin:20px 0;">

        <!-- ── General ── -->
        <div class="config-section">
            <h3 style="margin-bottom:12px;font-size:15px;">${l.general}</h3>
            ${fieldHtml('notification_language',   config.notification_language?.value   || 'de', d.notification_language)}
            ${fieldHtml('default_job_schedule',    config.default_job_schedule?.value    || '*/30 * * * *', d.default_job_schedule)}
        </div>

        <hr style="border:none;border-top:1px solid var(--border);margin:20px 0;">

        <!-- ── Matterbridge ── -->
        <div class="notification-section">
            <div style="display:flex;align-items:center;gap:14px;">
                <label class="toggle-switch">
                    <input type="checkbox" id="matterbridge-toggle"
                           data-key="matterbridge_enabled"
                           ${matterbridgeEnabled ? 'checked' : ''}
                           onchange="toggleNotificationSection('matterbridge-fields', this.checked)">
                    <span class="toggle-slider"></span>
                </label>
                <div>
                    <h3 style="font-size:15px;margin:0;">${l.matterbridge}</h3>
                    <p style="font-size:12px;color:var(--text-secondary);margin:2px 0 0;">${l.matterbridgeDesc}</p>
                </div>
            </div>
            <div id="matterbridge-fields" style="display:${matterbridgeEnabled ? 'block' : 'none'};" class="notification-section-fields">
                ${fieldHtml('matterbridge_url',      config.matterbridge_url?.value      || '', d.matterbridge_url)}
                ${fieldHtml('matterbridge_token',    config.matterbridge_token?.value    || '', d.matterbridge_token)}
                ${fieldHtml('matterbridge_gateway',  config.matterbridge_gateway?.value  || '', d.matterbridge_gateway)}
                ${fieldHtml('matterbridge_username', config.matterbridge_username?.value || '', d.matterbridge_username)}
            </div>
        </div>

        <div style="margin:12px 0;"></div>

        <!-- ── Apprise ── -->
        <div class="notification-section">
            <div style="display:flex;align-items:center;gap:14px;">
                <label class="toggle-switch">
                    <input type="checkbox" id="apprise-toggle"
                           data-key="apprise_enabled"
                           ${appriseEnabled ? 'checked' : ''}
                           onchange="toggleNotificationSection('apprise-fields', this.checked)">
                    <span class="toggle-slider"></span>
                </label>
                <div>
                    <h3 style="font-size:15px;margin:0;">${l.apprise}</h3>
                    <p style="font-size:12px;color:var(--text-secondary);margin:2px 0 0;">${l.appriseDesc}</p>
                </div>
            </div>
            <div id="apprise-fields" style="display:${appriseEnabled ? 'block' : 'none'};" class="notification-section-fields">
                ${fieldHtml('apprise_api_url',  config.apprise_api_url?.value  || '', d.apprise_api_url)}
                ${fieldHtml('apprise_api_key',  config.apprise_api_key?.value  || '', d.apprise_api_key)}
                ${fieldHtml('apprise_username', config.apprise_username?.value || '', d.apprise_username)}
                ${fieldHtml('apprise_password', config.apprise_password?.value || '', d.apprise_password)}
            </div>
        </div>
    `;
}

function toggleNotificationSection(id, enabled) {
    const el = document.getElementById(id);
    if (!el) return;

    // Prevent disabling both services at the same time
    if (!enabled) {
        const mbToggle = document.getElementById('matterbridge-toggle');
        const apToggle = document.getElementById('apprise-toggle');
        const otherId = id === 'matterbridge-fields' ? 'apprise-toggle' : 'matterbridge-toggle';
        const otherToggle = document.getElementById(otherId);
        if (otherToggle && !otherToggle.checked) {
            // Re-check the toggle that was just unchecked
            const thisToggle = document.getElementById(id === 'matterbridge-fields' ? 'matterbridge-toggle' : 'apprise-toggle');
            if (thisToggle) thisToggle.checked = true;
            const msg = currentLanguage === 'de'
                ? '⚠️ Mindestens ein Benachrichtigungsdienst muss aktiviert bleiben.'
                : '⚠️ At least one notification service must remain enabled.';
            showToast(msg, 'warning', 5000);
            return; // abort toggle
        }
    }

    if (enabled) {
        el.style.display = 'block';
        el.classList.add('notification-section-fields');
    } else {
        el.style.display = 'none';
    }
}

function updateConfigScheduleDescription(cronExpr) {
    const description = document.getElementById('configScheduleText');
    if (description) {
        const readable = cronToReadable(cronExpr);
        description.innerHTML = readable;
    }
}

async function saveConfig() {
    const inputs = document.querySelectorAll('#configForm input, #configForm select');
    const config = {};
    
    inputs.forEach(input => {
        if (!input.dataset.key) return; // skip inputs without data-key
        if (input.type === 'checkbox') {
            config[input.dataset.key] = input.checked ? 'true' : 'false';
        } else {
            config[input.dataset.key] = input.value;
        }
    });

    // Prevent saving when both notification services are disabled
    const mbToggle = document.getElementById('matterbridge-toggle');
    const apToggle = document.getElementById('apprise-toggle');
    if (mbToggle && apToggle && !mbToggle.checked && !apToggle.checked) {
        const msg = currentLanguage === 'de'
            ? '⚠️ Mindestens ein Benachrichtigungsdienst muss aktiviert sein (Matterbridge oder Apprise).'
            : '⚠️ At least one notification service must be enabled (Matterbridge or Apprise).';
        showToast(msg, 'warning', 6000);
        return; // abort save
    }

    try {
        await apiCall('/api/config', 'PUT', config);
        showToast(translations[currentLanguage].saveChanges + ' ✓', 'success');
    } catch (error) {
        showToast('Error: ' + error.message, 'error');
    }
}

// Health
async function loadHealth() {
    const t = translations[currentLanguage];
    document.getElementById('healthContent').innerHTML = '<div class="loading"><div class="spinner"></div></div>';

    try {
        const data = await apiCall('/api/health/services');
        renderHealth(data.services);
    } catch (error) {
        document.getElementById('healthContent').innerHTML = `<div class="alert alert-error">${t.error}</div>`;
    }
}

function renderHealth(services) {
    const t = translations[currentLanguage];
    const html = Object.entries(services).map(([name, service]) => {
        let badgeClass = 'badge-danger';
        let badgeText = t.error;
        if (service.status === 'ok') { badgeClass = 'badge-success'; badgeText = t.healthy; }
        else if (service.status === 'disabled') { badgeClass = 'badge-secondary'; badgeText = '— Disabled'; }
        else if (service.status === 'not_configured') { badgeClass = 'badge-secondary'; badgeText = '⚠ Not configured'; }

        return `
        <div class="card" style="margin-bottom: 16px; opacity: ${service.status === 'disabled' ? '0.5' : '1'};">
            <h3 style="margin-bottom: 12px;">${service.name || name.toUpperCase()}</h3>
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                <span class="badge ${badgeClass}">${badgeText}</span>
                ${service.url ? `<code>${service.url}</code>` : ''}
            </div>
            ${service.error ? `<div class="alert alert-error" style="margin-top:8px;">${service.error}</div>` : ''}
            ${service.data ? `<pre style="background: var(--bg); padding: 12px; border-radius: 6px; font-size: 12px; overflow-x: auto;">${JSON.stringify(service.data, null, 2)}</pre>` : ''}
        </div>`;
    }).join('');

    document.getElementById('healthContent').innerHTML = html;
}

// ============================================================================
// Multiple URL Management Functions
// ============================================================================

let urlFieldCounter = 0;

function addUrlField(value = '') {
    const container = document.getElementById('urlFieldsContainer');
    const fieldId = `urlField_${urlFieldCounter++}`;
    
    const fieldDiv = document.createElement('div');
    fieldDiv.className = 'url-field-wrapper';
    fieldDiv.id = fieldId;
    fieldDiv.style.cssText = 'display: flex; gap: 8px; margin-bottom: 8px;';
    
    const t = translations[currentLanguage];
    fieldDiv.innerHTML = `
        <input type="text" 
               class="url-input" 
               placeholder="${t.urlPlaceholder}" 
               value="${value}"
               style="flex: 1;"
               required>
        <button type="button" 
                class="btn btn-danger btn-sm" 
                onclick="removeUrlField('${fieldId}')"
                style="padding: 6px 12px;"
                ${container.children.length === 0 ? 'disabled' : ''}>
            ✕
        </button>
    `;
    
    container.appendChild(fieldDiv);
    
    // Update remove buttons state
    updateRemoveButtons();
}

function removeUrlField(fieldId) {
    const field = document.getElementById(fieldId);
    if (field) {
        field.remove();
    }
    updateRemoveButtons();
}

function updateRemoveButtons() {
    const container = document.getElementById('urlFieldsContainer');
    const fields = container.querySelectorAll('.url-field-wrapper');
    
    // Disable remove button on first field if it's the only one
    fields.forEach((field, index) => {
        const removeBtn = field.querySelector('button');
        if (removeBtn) {
            removeBtn.disabled = fields.length === 1;
        }
    });
}

function getUrlsFromFields() {
    const inputs = document.querySelectorAll('.url-input');
    const urls = Array.from(inputs)
        .map(input => input.value.trim())
        .filter(url => url.length > 0);
    return urls.join(',');
}

function setUrlsToFields(urlString) {
    const container = document.getElementById('urlFieldsContainer');
    container.innerHTML = ''; // Clear existing fields
    urlFieldCounter = 0;
    
    const urls = urlString.split(',').map(u => u.trim()).filter(u => u);
    
    if (urls.length === 0) {
        addUrlField(); // Add at least one empty field
    } else {
        urls.forEach(url => addUrlField(url));
    }
}

function formatUrlsForDisplay(urlString) {
    const urls = urlString.split(',').map(u => u.trim()).filter(u => u);
    
    if (urls.length <= 1) {
        return `<code style="font-size: 12px;">${urlString}</code>`;
    }
    
    // Format as "URL1 OR URL2 OR URL3"
    const formatted = urls.map(url => `<code style="font-size: 11px;">${url}</code>`).join(' <strong>OR</strong> ');
    return `<div style="max-width: 400px; line-height: 1.6;">${formatted}</div>`;
}

// ============================================================================
// Password Change Functions
// ============================================================================

function showChangePasswordModal() {
    const t = translations[currentLanguage];
    
    // Update all text elements with translations
    document.getElementById('changePasswordTitle').textContent = '🔐 ' + t.changePassword;
    document.getElementById('currentPasswordLabel').textContent = t.currentPassword + ' *';
    document.getElementById('newPasswordLabel').textContent = t.newPassword + ' *';
    document.getElementById('confirmPasswordLabel').textContent = t.confirmNewPassword + ' *';
    document.getElementById('changePasswordBtnText').textContent = t.changePassword;
    document.getElementById('passwordCancelBtn').textContent = t.cancel;
    
    // Update requirements text
    document.getElementById('passwordRequirements').innerHTML = `
        <strong>${t.requirements}</strong><br>
        • ${t.minChars}<br>
        • ${t.mustContain}<br>
        • ${t.mustDiffer}
    `;
    
    // Update note
    document.getElementById('passwordChangeNote').innerHTML = t.passwordChangeNote;
    
    // Reset form
    document.getElementById('changePasswordForm').reset();
    document.getElementById('passwordError').style.display = 'none';
    document.getElementById('passwordSuccess').style.display = 'none';
    document.getElementById('changePasswordModal').classList.add('active');
}

function closeChangePasswordModal() {
    document.getElementById('changePasswordModal').classList.remove('active');
}

async function handleChangePassword(e) {
    e.preventDefault();
    
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    const errorDiv = document.getElementById('passwordError');
    errorDiv.style.display = 'none';
    
    // Validate current password is provided
    if (!currentPassword || currentPassword.trim() === '') {
        errorDiv.textContent = 'Current password is required';
        errorDiv.style.display = 'block';
        return;
    }
    
    // Validate new password is provided
    if (!newPassword || newPassword.trim() === '') {
        errorDiv.textContent = 'New password is required';
        errorDiv.style.display = 'block';
        return;
    }
    
    // Validate password length (minimum 6 characters)
    if (newPassword.length < 6) {
        errorDiv.textContent = 'New password must be at least 6 characters long';
        errorDiv.style.display = 'block';
        return;
    }
    
    // Validate password strength (at least one number or special character recommended)
    const hasNumberOrSpecial = /[0-9!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(newPassword);
    if (!hasNumberOrSpecial) {
        errorDiv.textContent = 'New password should contain at least one number or special character for better security';
        errorDiv.style.display = 'block';
        return;
    }
    
    // Validate passwords match
    if (newPassword !== confirmPassword) {
        errorDiv.textContent = 'New passwords do not match';
        errorDiv.style.display = 'block';
        return;
    }
    
    // Check if new password is same as current (optional but recommended)
    if (newPassword === currentPassword) {
        errorDiv.textContent = 'New password must be different from current password';
        errorDiv.style.display = 'block';
        return;
    }
    
    document.getElementById('changePasswordBtnText').style.display = 'none';
    document.getElementById('changePasswordSpinner').style.display = 'block';
    
    try {
        const response = await apiCall('/api/auth/change-password', 'POST', {
            current_password: currentPassword,
            new_password: newPassword
        });
        
        // Hide error, show success message, hide form
        errorDiv.style.display = 'none';
        document.getElementById('changePasswordForm').style.display = 'none';
        document.getElementById('changePasswordBtnText').style.display = 'block';
        document.getElementById('changePasswordSpinner').style.display = 'none';
        
        const t = translations[currentLanguage];
        const successDiv = document.getElementById('passwordSuccess');
        successDiv.textContent = '✅ ' + t.passwordChanged;
        successDiv.style.display = 'block';
        
        // Redirect to login after 2 seconds
        setTimeout(() => {
            closeChangePasswordModal();
            successDiv.style.display = 'none';
            document.getElementById('changePasswordForm').style.display = 'block';
            logout();
        }, 2000);
        
    } catch (error) {
        errorDiv.textContent = error.message || 'Failed to change password';
        errorDiv.style.display = 'block';
        document.getElementById('changePasswordBtnText').style.display = 'block';
        document.getElementById('changePasswordSpinner').style.display = 'none';
    }
}

// ============================================================================
// Password Visibility Toggle
// ============================================================================

function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    const button = input.nextElementSibling; // Get the eye button
    
    if (input.type === 'password') {
        input.type = 'text';
        button.textContent = '👁️'; // Open eye (visible)
    } else {
        input.type = 'password';
        button.textContent = '🙈'; // Closed eye (hidden)
    }
}

// Event listener is set up in setupEventListeners() function called on DOMContentLoaded
