// Función para mostrar mensajes informativos
function showActionMessage(message) {
    const container = document.getElementById('messages-container');

    const messageBox = document.createElement('div');
    messageBox.className = 'action-message';
    messageBox.textContent = message;
    messageBox.style.animation = 'slideIn 0.4s forwards';
    
    container.appendChild(messageBox);
    
    setTimeout(() => {
        messageBox.style.animation = 'slideOut 7s forwards';
        
        setTimeout(() => {
            messageBox.remove();
        }, 7000);
    }, 7400);
}

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

        const response = await fetch(`/api${endpoint}`, options);
        const data = await response.json();
        
        responseBox.textContent = JSON.stringify(data, null, 2);
        return data;
    } catch (error) {
        const responseBox = document.getElementById('api-response');
        responseBox.textContent = JSON.stringify({ error: error.message }, null, 2);
    }
}

// Update ANY Honeypot status UI
function updateStatusUI(elementIdRunning, elementIdInstalled, elementIdConfigured, isRunning, isInstalled, isConfigured, buttonStart, buttonStop, buttonInstall, buttonConfigure) {
    const UIRunning = document.getElementById(elementIdRunning);
    const UIInstalled = document.getElementById(elementIdInstalled);
    const UIConfigured = elementIdConfigured ? document.getElementById(elementIdConfigured) : null;
    const startBtn = document.getElementById(buttonStart);
    const stopBtn = document.getElementById(buttonStop);
    const installBtn = document.getElementById(buttonInstall);
    const configureBtn = buttonConfigure ? document.getElementById(buttonConfigure) : null;
    if (isInstalled) {
        UIInstalled.textContent = 'Installed';
        UIInstalled.className = 'status-ui installed';
        installBtn.disabled = true;
        installBtn.classList.add('disabled');
        if (configureBtn) {
            configureBtn.disabled = false;
            configureBtn.classList.remove('disabled');
        }
        startBtn.disabled = false;
        startBtn.classList.remove('disabled');
        stopBtn.disabled = false;
        stopBtn.classList.remove('disabled');
        if (isRunning) {
            UIRunning.textContent = 'Running';
            UIRunning.className = 'status-ui running';
            startBtn.disabled = true;
            startBtn.classList.add('disabled');
            stopBtn.disabled = false;
            stopBtn.classList.remove('disabled');
        } else {
            UIRunning.textContent = 'Stopped';
            UIRunning.className = 'status-ui stopped';
            startBtn.disabled = false;
            startBtn.classList.remove('disabled');
            stopBtn.disabled = true;
            stopBtn.classList.add('disabled');
        }
        if (isConfigured) {
            startBtn.disabled = false;
            startBtn.classList.remove('disabled');
            UIConfigured.textContent = 'Configured';
            UIConfigured.className = 'status-ui configured';
            configureBtn.disabled = true;
            configureBtn.classList.add('disabled');
        } else {
            if (UIConfigured && configureBtn) {
                startBtn.disabled = true;
                startBtn.classList.add('disabled');
                UIConfigured.textContent = 'Not Configured';
                UIConfigured.className = 'status-ui not-configured';
                configureBtn.disabled = false;
                configureBtn.classList.remove('disabled');
            }
        }
    } else {
        UIInstalled.textContent = 'Not Installed';
        UIInstalled.className = 'status-ui not-installed';
        installBtn.disabled = false;
        installBtn.classList.remove('disabled');
        if (configureBtn) {
            configureBtn.disabled = true;
            configureBtn.classList.add('disabled');
        }
        startBtn.disabled = true;
        startBtn.classList.add('disabled');
        stopBtn.disabled = true;
        stopBtn.classList.add('disabled');
    }
}

function updateStatusSplunk(elementIdRunning, elementIdInstalled, elementIdToken, isRunning, isInstalled, tokenDetected) {
    const UIRunning = document.getElementById(elementIdRunning);
    const UIInstalled = document.getElementById(elementIdInstalled);
    const UIToken = document.getElementById(elementIdToken);
    const startBtn = document.getElementById('splunk-start-btn');
    const stopBtn = document.getElementById('splunk-stop-btn');
    const createTokenBtn = document.getElementById('create-token-btn');
    if (isInstalled) {
        UIInstalled.textContent = 'Installed';
        UIInstalled.className = 'status-ui installed';
        startBtn.disabled = false;
        startBtn.classList.remove('disabled');
        if (isRunning) {
            UIRunning.textContent = 'Running';
            UIRunning.className = 'status-ui running';
            startBtn.disabled = true;
            startBtn.classList.add('disabled');
            stopBtn.disabled = false;
            stopBtn.classList.remove('disabled');
            if (tokenDetected) {
                UIToken.textContent = 'Token OK';
                UIToken.className = 'status-ui configured';
                createTokenBtn.disabled = true;
                createTokenBtn.classList.add('disabled');
            } else {
                UIToken.textContent = 'NO Token';
                UIToken.className = 'status-ui not-configured';
                createTokenBtn.disabled = false;
                createTokenBtn.classList.remove('disabled');
            }
        } else {
            UIRunning.textContent = 'Stopped';
            UIRunning.className = 'status-ui stopped';
            startBtn.disabled = false;
            startBtn.classList.remove('disabled');
            stopBtn.disabled = true;
            stopBtn.classList.add('disabled');
            createTokenBtn.disabled = true;
            createTokenBtn.classList.add('disabled');
        }
    } else {
        UIInstalled.textContent = 'Not Installed';
        UIInstalled.className = 'status-ui not-installed';
        startBtn.disabled = true;
        startBtn.classList.add('disabled');
        stopBtn.disabled = true;
        stopBtn.classList.add('disabled');
        createTokenBtn.disabled = true;
        createTokenBtn.classList.add('disabled');
    }
}

// Cowrie Functions
async function checkCowrieStatus() {
    try {
        const response = await makeRequest('/cowrie/status');
        updateStatusUI('cowrie-status', 'cowrie-installed', 'cowrie-configured', response.running, response.installed, response.configured, 'cowrie-start-btn', 'cowrie-stop-btn', 'cowrie-install-btn', 'cowrie-configure-btn');
        if (response.installed) {
            document.getElementById('custom-path').value = response.cowrie_path || '';
        }
    } catch (error) {
        showActionMessage('Error checking Cowrie Honeypot status: ' + error.message);
    }
}

async function startCowrie() {
    try {
        showActionMessage('Starting Cowrie Honeypot...');
        const response = await makeRequest('/cowrie/start', 'POST');
        const statusResponse = await makeRequest('/cowrie/status');
        if (response.success) {
            showActionMessage('Cowrie Honeypot started successfully. Listening on port 22.');
            updateStatusUI('cowrie-status', 'cowrie-installed', 'cowrie-configured', statusResponse.running, statusResponse.installed, statusResponse.configured, 'cowrie-start-btn', 'cowrie-stop-btn', 'cowrie-install-btn', 'cowrie-configure-btn');
        }
    } catch (error) {
        showActionMessage('Error starting Cowrie Honeypot: ' + error.message);
    }
}

async function stopCowrie() {
    try {
        showActionMessage('Stopping Cowrie Honeypot...');
        const response = await makeRequest('/cowrie/stop', 'POST');
        const statusResponse = await makeRequest('/cowrie/status');       
        if (response.success) {
            showActionMessage('Cowrie Honeypot stopped successfully.');
            updateStatusUI('cowrie-status', 'cowrie-installed', 'cowrie-configured', statusResponse.running, statusResponse.installed, statusResponse.configured, 'cowrie-start-btn', 'cowrie-stop-btn', 'cowrie-install-btn', 'cowrie-configure-btn');
        }
    } catch (error) {
        showActionMessage('Error stopping Cowrie Honeypot: ' + error.message);
    }
}

async function setCustomPath() {
    const path = document.getElementById('custom-path').value;
    if (!path) {
        showActionMessage('Please enter a valid path for Cowrie Honeypot.');
        return;
    }
    try {
        const response = await makeRequest('/cowrie/set-path', 'POST', { path: path });
        if (response.success) {
            showActionMessage('Custom path for Cowrie Honeypot set successfully.');
            const statusResponse = await makeRequest('/cowrie/status');
            updateStatusUI('cowrie-status', 'cowrie-installed', 'cowrie-configured', statusResponse.running, statusResponse.installed, statusResponse.configured, 'cowrie-start-btn', 'cowrie-stop-btn', 'cowrie-install-btn', 'cowrie-configure-btn');
        } else {
            showActionMessage(path + ' is not a valid path for Cowrie Honeypot. Please enter a valid path.');
        }
    } catch (error) {
        showActionMessage('Error setting custom path for Cowrie Honeypot: ' + error.message);
    }
}

async function installCowrie() {
    try {
        showActionMessage('Installing Cowrie Honeypot... This may take a few minutes.');
        const response = await makeRequest('/cowrie/install', 'POST');
        const statusResponse = await makeRequest('/cowrie/status');
        if (response.success) {
            showActionMessage('Cowrie Honeypot installed successfully.');
            showActionMessage('You can find Cowrie logs in ' + response.path + '/var/log/cowrie')
            updateStatusUI('cowrie-status', 'cowrie-installed', 'cowrie-configured', statusResponse.running, statusResponse.installed, statusResponse.configured, 'cowrie-start-btn', 'cowrie-stop-btn', 'cowrie-install-btn', 'cowrie-configure-btn');            
        }
    } catch (error) {
        showActionMessage('Error installing Cowrie Honeypot: ' + error.message);
    }
}

async function configureCowrie() {
    try {
        showActionMessage('Configuring Cowrie Honeypot...');
        const response = await makeRequest('/cowrie/configure', 'POST');
        const statusResponse = await makeRequest('/cowrie/status');
        if (response.success) {
            showActionMessage('Cowrie Honeypot configured successfully.');
            updateStatusUI('cowrie-status', 'cowrie-installed', 'cowrie-configured', statusResponse.running, statusResponse.installed, statusResponse.configured, 'cowrie-start-btn', 'cowrie-stop-btn', 'cowrie-install-btn', 'cowrie-configure-btn');            
        }
    } catch (error) {
        showActionMessage('Error configuring Cowrie Honeypot: ' + error.message);
    }
}

async function configureSSH() {
    try {
        showActionMessage('Configuring SSH redirect for Cowrie Honeypot...');
        const response = await makeRequest('/cowrie/setup-redirect', 'POST');
        const statusResponse = await makeRequest('/cowrie/status');
        if (response.success) {
            showActionMessage('SSH redirect for Cowrie Honeypot configured successfully.');
            updateStatusUI('cowrie-status', 'cowrie-installed', 'cowrie-configured', statusResponse.running, statusResponse.installed, statusResponse.configured, 'cowrie-start-btn', 'cowrie-stop-btn', 'cowrie-install-btn', 'cowrie-configure-btn');            
        }
    } catch (error) {
        showActionMessage('Error configuring SSH redirect for Cowrie Honeypot: ' + error.message);
    }
}

async function cleanupCowrie() {
    try {
        showActionMessage('Restoring Cowrie configuration, deleting iptables, stopping ssh...');
        const response = await makeRequest('/cowrie/cleanup', 'POST');
        const statusResponse = await makeRequest('/cowrie/status');
        if (response.success) {
            showActionMessage('Cowrie Honeypot restored successfully.');
            updateStatusUI('cowrie-status', 'cowrie-installed', 'cowrie-configured', statusResponse.running, statusResponse.installed, statusResponse.configured, 'cowrie-start-btn', 'cowrie-stop-btn', 'cowrie-install-btn', 'cowrie-configure-btn');            
        }
    } catch (error) {
        showActionMessage('Error restoring Cowrie Honeypot: ' + error.message);
    }
}

// Dionaea Functions
async function checkDionaeaStatus() {
    try {
        const response = await makeRequest('/dionaea/status');
        updateStatusUI('dionaea-status', 'dionaea-installed', null, response.running, response.installed, null, 'dionaea-start-btn', 'dionaea-stop-btn', 'dionaea-install-btn', null);
    } catch (error) {
        showActionMessage('Error checking Dionaea Honeypot status: ' + error.message);
    }
}

async function installDionaea() {
    try {
        showActionMessage('Installing Dionaea Honeypot... This may take a few minutes.');
        const response = await makeRequest('/dionaea/install', 'POST');
        const statusResponse = await makeRequest('/dionaea/status');
        if (response.success) {
            showActionMessage('Dionaea Honeypot installed successfully.');
            showActionMessage('Dionaea docker container name: ' + response.container_name);
            showActionMessage('You can find Dionaea logs and binaries in: ' + response.data_dir);
            updateStatusUI('dionaea-status', 'dionaea-installed', null, statusResponse.running, statusResponse.installed, null, 'dionaea-start-btn', 'dionaea-stop-btn', 'dionaea-install-btn', null);            
        }
    } catch (error) {
        showActionMessage('Error installing Dionaea Honeypot: ' + error.message);
    }
}

async function startDionaea() {
    try {
        showActionMessage('Starting Dionaea Honeypot...');
        const response = await makeRequest('/dionaea/start', 'POST');
        if (response.success) {
            showActionMessage('Dionaea Honeypot started successfully. Listening on ports 21, 23, 42, 80, 135, 443, 445, 1433, 1723, 1883, 1900/udp, 3306, 5060, 5060/udp, 5061, 11211.');
            checkDionaeaStatus();
        } else {
            showActionMessage('Error: ' + (response.message || 'Unknown error'));
        }
    } catch (error) {
        showActionMessage('Error starting Dionaea Honeypot: ' + error.message);
    }
}

async function stopDionaea() {
    try {
        showActionMessage('Stopping Dionaea Honeypot...');
        const response = await makeRequest('/dionaea/stop', 'POST');
        if (response.success) {
            showActionMessage('Dionaea Honeypot stopped successfully.');
            checkDionaeaStatus();
        } else {
            showActionMessage('Error: ' + (response.message || 'Unknown error'));
        }
    } catch (error) {
        showActionMessage('Error stopping Dionaea Honeypot: ' + error.message);
    }
}

// Splunk Functions
async function checkSplunkStatus() {
    try {
        const response = await makeRequest('/splunk/status');
        updateStatusSplunk('splunk-status', 'splunk-installed', 'splunk-token', response.running, response.installed, response.token);
    } catch (error) {
        showActionMessage('Error checking Splunk SIEM status: ' + error.message);
    }
}

async function startSplunk() {
    try {
        showActionMessage('Starting Splunk SIEM...');
        const response = await makeRequest('/splunk/start', 'POST');
        const statusResponse = await makeRequest('/splunk/status');
        if (response.success) {
            updateStatusSplunk('splunk-status', 'splunk-installed', 'splunk-token', statusResponse.running, statusResponse.installed, statusResponse.token);
        }
    } catch (error) {
        showActionMessage('Error starting Splunk SIEM: ' + error.message);
    }
}

async function stopSplunk() {
    try {
        showActionMessage('Stopping Splunk SIEM...');
        const response = await makeRequest('/splunk/stop', 'POST');
        const statusResponse = await makeRequest('/splunk/status');
        if (response.success) {
            updateStatusSplunk('splunk-status', 'splunk-installed', 'splunk-token', statusResponse.running, statusResponse.installed, statusResponse.token);
        }
    } catch (error) {
        showActionMessage('Error stopping Splunk SIEM: ' + error.message);
    }
}

// Auto-refresh status on page load
window.addEventListener('DOMContentLoaded', () => {
    checkCowrieStatus();
    checkDionaeaStatus();
    checkSplunkStatus();
});
