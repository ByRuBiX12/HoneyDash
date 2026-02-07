// API Base URL
const API_URL = 'http://localhost:5000/api';

// Función auxiliar para hacer peticiones
async function makeRequest(endpoint, method = 'GET', body = null) {
    const responseBox = document.getElementById('api-response');
    responseBox.textContent = 'Cargando...';

    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(`${API_URL}${endpoint}`, options);
        const data = await response.json();
        
        responseBox.textContent = JSON.stringify(data, null, 2);
        return data;
    } catch (error) {
        const responseBox = document.getElementById('api-response');
        responseBox.textContent = JSON.stringify({ error: error.message }, null, 2);
    }
}

// Update status UI
function updateStatusUI(elementIdRunning, elementIdInstalled, elementIdConfigured, isRunning, isInstalled, isConfigured) {
    const UIRunning = document.getElementById(elementIdRunning);
    const UIInstalled = document.getElementById(elementIdInstalled);
    const UIConfigured = document.getElementById(elementIdConfigured);
    if (isRunning) {
        UIRunning.textContent = 'Running';
        UIRunning.className = 'status-ui running';
    } else {
        UIRunning.textContent = 'Stopped';
        UIRunning.className = 'status-ui stopped';
    }
    if (isInstalled) {
        UIInstalled.textContent = 'Installed';
        UIInstalled.className = 'status-ui installed';
    } else {
        UIInstalled.textContent = 'Not Installed';
        UIInstalled.className = 'status-ui not-installed';
    }
    if (isConfigured) {
        UIConfigured.textContent = 'Configured';
        UIConfigured.className = 'status-ui configured';
    } else {
        UIConfigured.textContent = 'Not Configured';
        UIConfigured.className = 'status-ui not-configured';
    }
}

function updateStatusSplunk(elementIdRunning, elementIdInstalled, elementIdToken, isRunning, isInstalled, tokenDetected) {
    const UIRunning = document.getElementById(elementIdRunning);
    const UIInstalled = document.getElementById(elementIdInstalled);
    const UIToken = document.getElementById(elementIdToken);
    if (isRunning) {
        UIRunning.textContent = 'Running';
        UIRunning.className = 'status-ui running';
    } else {
        UIRunning.textContent = 'Stopped';
        UIRunning.className = 'status-ui stopped';
    }
    if (isInstalled) {
        UIInstalled.textContent = 'Installed';
        UIInstalled.className = 'status-ui installed';
    } else {
        UIInstalled.textContent = 'Not Installed';
        UIInstalled.className = 'status-ui not-installed';
    }
    if (tokenDetected) {
        UIToken.textContent = 'Token OK';
        UIToken.className = 'status-ui configured';
    } else {
        UIToken.textContent = 'NO Token';
        UIToken.className = 'status-ui not-configured';
    }
}

// Cowrie Functions
async function checkCowrieStatus() {
    try {
        const response = await makeRequest('/cowrie/status');
        updateStatusUI('cowrie-status', 'cowrie-installed', 'cowrie-configured', response.running, response.installed, response.configured);
        if (response.installed) {
            document.getElementById('custom-path').value = response.cowrie_path || '';
        }
    } catch (error) {
        alert('Error checking Cowrie Honeypot status: ' + error.message);
    }
}

async function startCowrie() {
    try {
        const response = await makeRequest('/cowrie/start', 'POST');
        const statusResponse = await makeRequest('/cowrie/status');
        if (response.success) {
            updateStatusUI('cowrie-status', 'cowrie-installed', 'cowrie-configured', statusResponse.running, statusResponse.installed, statusResponse.configured);
        }
    } catch (error) {
        alert('Error starting Cowrie Honeypot: ' + error.message);
    }
}

async function stopCowrie() {
    try {
        const response = await makeRequest('/cowrie/stop', 'POST');
        const statusResponse = await makeRequest('/cowrie/status');
        if (response.success) {
            updateStatusUI('cowrie-status', 'cowrie-installed', 'cowrie-configured', statusResponse.running, statusResponse.installed, statusResponse.configured);
        }
    } catch (error) {
        alert('Error stopping Cowrie Honeypot: ' + error.message);
    }
}

async function setCustomPath() {
    const path = document.getElementById('custom-path').value;
    if (!path) {
        alert('Por favor, ingresa una ruta');
        return;
    }
    try {
        const response = await makeRequest('/cowrie/set-path', 'POST', { path: path });
    } catch (error) {
        alert('Error setting custom path for Cowrie Honeypot: ' + error.message);
    }
}

async function installCowrie() {
    try {
        const response = await makeRequest('/cowrie/install', 'POST');
        const statusResponse = await makeRequest('/cowrie/status');
        if (response.success) {
            updateStatusUI('cowrie-status', 'cowrie-installed', 'cowrie-configured', statusResponse.running, statusResponse.installed, statusResponse.configured);            
        }
    } catch (error) {
        alert('Error installing Cowrie Honeypot: ' + error.message);
    }
}

async function configureCowrie() {
    try {
        const response = await makeRequest('/cowrie/configure', 'POST');
        const statusResponse = await makeRequest('/cowrie/status');
        if (response.success) {
            updateStatusUI('cowrie-status', 'cowrie-installed', 'cowrie-configured', statusResponse.running, statusResponse.installed, statusResponse.configured);            
        }
    } catch (error) {
        alert('Error configuring Cowrie Honeypot: ' + error.message);
    }
}

async function configureSSH() {
    try {
        const response = await makeRequest('/cowrie/setup-redirect', 'POST');
        const statusResponse = await makeRequest('/cowrie/status');
        if (response.success) {
            updateStatusUI('cowrie-status', 'cowrie-installed', 'cowrie-configured', statusResponse.running, statusResponse.installed, statusResponse.configured);            
        }
    } catch (error) {
        alert('Error configuring SSH redirect for Cowrie Honeypot: ' + error.message);
    }
}

async function cleanupCowrie() {
    try {
        const response = await makeRequest('/cowrie/cleanup', 'POST');
        const statusResponse = await makeRequest('/cowrie/status');
        if (response.success) {
            updateStatusUI('cowrie-status', 'cowrie-installed', 'cowrie-configured', statusResponse.running, statusResponse.installed, statusResponse.configured);            
        }
    } catch (error) {
        alert('Error restoring Cowrie Honeypot: ' + error.message);
    }
}

// Splunk Functions
async function checkSplunkStatus() {
    try {
        const response = await makeRequest('/splunk/status');
        updateStatusSplunk('splunk-status', 'splunk-installed', 'splunk-token', response.running, response.installed, response.token);
    } catch (error) {
        alert('Error checking Splunk SIEM status: ' + error.message);
    }
}

async function startSplunk() {
    try {
        const response = await makeRequest('/splunk/start', 'POST');
        const statusResponse = await makeRequest('/splunk/status');
        if (response.success) {
            updateStatusSplunk('splunk-status', 'splunk-installed', 'splunk-token', statusResponse.running, statusResponse.installed, statusResponse.token);
        }
    } catch (error) {
        alert('Error starting Splunk SIEM: ' + error.message);
    }
}

async function stopSplunk() {
    try {
        const response = await makeRequest('/splunk/stop', 'POST');
        const statusResponse = await makeRequest('/splunk/status');
        if (response.success) {
            updateStatusSplunk('splunk-status', 'splunk-installed', 'splunk-token', statusResponse.running, statusResponse.installed, statusResponse.token);
        }
    } catch (error) {
        alert('Error stopping Splunk SIEM: ' + error.message);
    }
}

// Auto-refresh status on page load
window.addEventListener('DOMContentLoaded', () => {
    checkCowrieStatus();
    checkSplunkStatus();
});
