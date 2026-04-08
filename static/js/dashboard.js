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

function togglePasswordVisibility(inputId, toggleBtn) {
    const passwordInput = document.getElementById(inputId);
    if (!passwordInput) {
        return;
    }

    if (toggleBtn) {
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
        } else {
            passwordInput.type = 'password';
        }
    }
}

// Función auxiliar para hacer peticiones
async function makeRequest(endpoint, method = 'GET', body = null) {
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

        return data;
    } catch (error) {
        console.error('Error making request to ' + endpoint + ':', error);
    }
}

// Update ANY Honeypot & Suricata status UI
function updateStatusUI(elementIdRunning, elementIdInstalled, elementIdConfigured, isRunning, isInstalled, isConfigured, buttonStart, buttonStop, buttonInstall, buttonConfigure) {
    const UIRunning = document.getElementById(elementIdRunning);
    const UIInstalled = document.getElementById(elementIdInstalled);
    const UIConfigured = elementIdConfigured ? document.getElementById(elementIdConfigured) : null;
    const startBtn = document.getElementById(buttonStart);
    const stopBtn = document.getElementById(buttonStop);
    const installBtn = buttonInstall ? document.getElementById(buttonInstall) : null;
    const configureBtn = buttonConfigure ? document.getElementById(buttonConfigure) : null;
    if (isInstalled) {
        UIInstalled.textContent = 'Installed';
        UIInstalled.className = 'status-ui installed';
        if (installBtn) {
            installBtn.disabled = true;
            installBtn.classList.add('disabled');
        }
        if (configureBtn) {
            configureBtn.disabled = false;
            configureBtn.classList.remove('disabled');
        }
        startBtn.disabled = false;
        startBtn.classList.remove('disabled');
        stopBtn.disabled = false;
        stopBtn.classList.remove('disabled');
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
            stopBtn.disabled = true;
            stopBtn.classList.add('disabled');
        }
    } else {
        UIInstalled.textContent = 'Not Installed';
        UIInstalled.className = 'status-ui not-installed';
        if (installBtn) {
            installBtn.disabled = false;
            installBtn.classList.remove('disabled');
        }
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

function updateStatusSplunk(elementIdRunning, elementIdInstalled, elementIdToken, elementIdCreds, isRunning, isInstalled, tokenDetected, creds, user, password) {
    const UIRunning = document.getElementById(elementIdRunning);
    const UIInstalled = document.getElementById(elementIdInstalled);
    const UIToken = document.getElementById(elementIdToken);
    const UICreds = document.getElementById(elementIdCreds);
    const startBtn = document.getElementById('splunk-start-btn');
    const stopBtn = document.getElementById('splunk-stop-btn');
    const createTokenBtn = document.getElementById('create-token-btn');
    const userInput = document.getElementById('splunk-user');
    const passwordInput = document.getElementById('splunk-password');
    userInput.value = user;
    passwordInput.value = password;
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
                if (creds) {
                    UICreds.textContent = 'Creds OK';
                    UICreds.className = 'status-ui configured';
                } else {
                    UICreds.textContent = 'NO creds';
                    UICreds.className = 'status-ui not-configured';
                }
            } else {
                UIToken.textContent = 'NO Token';
                UIToken.className = 'status-ui not-configured';
                createTokenBtn.disabled = false;
                createTokenBtn.classList.remove('disabled');
                if (creds) {
                    UICreds.textContent = 'Creds OK';
                    UICreds.className = 'status-ui configured';
                } else {
                    UICreds.textContent = 'NO creds';
                    UICreds.className = 'status-ui not-configured';
                    createTokenBtn.disabled = true;
                    createTokenBtn.classList.add('disabled');
                }
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
            if (creds) {
                UICreds.textContent = 'Creds OK';
                UICreds.className = 'status-ui configured';
            } else {
                UICreds.textContent = 'NO creds';
                UICreds.className = 'status-ui not-configured';
            }
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
        UICreds.textContent = 'NO creds';
        UICreds.className = 'status-ui not-configured';
    }
}

// Cowrie Functions
async function checkCowrieStatus() {
    try {
        const response = await makeRequest('/cowrie/status');
        updateStatusUI('cowrie-status', 'cowrie-installed', 'cowrie-configured', response.running, response.installed, response.configured, 'cowrie-start-btn', 'cowrie-stop-btn', 'cowrie-install-btn', 'cowrie-configure-btn');
        if (response.installed) {
            document.getElementById('cowrie-custom-path').value = response.cowrie_path || '';
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

// Cowrie, Splunk & Suricata manually set path function
async function setCustomPath(service) {
    const path = document.getElementById(`${service}-custom-path`).value;
    let name = "";
    if (service === 'cowrie') {
        name = "Cowrie";
    } else if (service === 'splunk') {
        name = "Splunk";
    } else if (service === 'suricata') {
        name = "Suricata";
    }
    if (!path) {
        showActionMessage('Please enter a valid path for ' + name + '.');
        return;
    }
    try {
        const response = await makeRequest(`/${service}/set-path`, 'POST', { path: path });
        if (response.success) {
            showActionMessage(`Custom path for ${name} set successfully.`);
            document.getElementById(`set-${service}-path-btn`).disabled = true;
            document.getElementById(`set-${service}-path-btn`).classList.add('disabled');
        } else {
            showActionMessage(path + ' is not a valid path for ' + name + ' Honeypot. Please enter a valid path.');
        }
        const statusResponse = await makeRequest(`/${service}/status`);
            if (service === 'splunk') {
                updateStatusSplunk(`${service}-status`, `${service}-installed`, `${service}-token`, `${service}-creds`, statusResponse.running, statusResponse.installed, statusResponse.token, statusResponse.creds, statusResponse.user, statusResponse.password);
            } else if (service === 'cowrie') {
                updateStatusUI(`${service}-status`, `${service}-installed`, `${service}-configured`, statusResponse.running, statusResponse.installed, statusResponse.configured, `${service}-start-btn`, `${service}-stop-btn`, `${service}-install-btn`, `${service}-configure-btn`);
            } else { // Suricata
                updateStatusUI(`${service}-status`, `${service}-installed`, null, statusResponse.running, statusResponse.installed, null, `${service}-start-btn`, `${service}-stop-btn`, null, null);
            }
    } catch (error) {
        showActionMessage(`Error setting custom path for ${name}: ` + error.message);
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

// DDoSPot Functions
async function checkDDoSPotStatus() {
    try {
        const response = await makeRequest('/ddospot/status');
        updateStatusUI('ddospot-status', 'ddospot-installed', null, response.running, response.installed, null, 'ddospot-start-btn', 'ddospot-stop-btn', 'ddospot-install-btn', null);
    } catch (error) {
        showActionMessage('Error checking DDoSPot Honeypot status: ' + error.message);
    }
}

async function installDDoSPot() {
    try {
        showActionMessage('Installing DDoSPot Honeypot... This may take a few minutes.');
        const response = await makeRequest('/ddospot/install', 'POST');
        const statusResponse = await makeRequest('/ddospot/status');
        if (response.success) {
            showActionMessage('DDoSPot Honeypot installed successfully.');
            showActionMessage('DDoSPot docker container name: ' + response.container_name);
            showActionMessage('You can find DDoSPot logs and binaries in: ' + response.data_dir);
            updateStatusUI('ddospot-status', 'ddospot-installed', null, statusResponse.running, statusResponse.installed, null, 'ddospot-start-btn', 'ddospot-stop-btn', 'ddospot-install-btn', null);            
        }
    } catch (error) {
        showActionMessage('Error installing DDoSPot Honeypot: ' + error.message);
    }
}

async function startDDoSPot() {
    try {
        showActionMessage('Starting DDoSPot Honeypot...');
        const response = await makeRequest('/ddospot/start', 'POST');
        if (response.success) {
            showActionMessage('DDoSPot Honeypot started successfully. Listening on ports 19/udp, 53/tcp/udp, 123/udp, 161/udp, 1900/udp.');
            checkDDoSPotStatus();
        } else {
            showActionMessage('Error: ' + (response.message || 'Unknown error'));
        }
    } catch (error) {
        showActionMessage('Error starting DDoSPot Honeypot: ' + error.message);
    }
}

async function stopDDoSPot() {
    try {
        showActionMessage('Stopping DDoSPot Honeypot...');
        const response = await makeRequest('/ddospot/stop', 'POST');
        if (response.success) {
            showActionMessage('DDoSPot Honeypot stopped successfully.');
            checkDDoSPotStatus();
        } else {
            showActionMessage('Error: ' + (response.message || 'Unknown error'));
        }
    } catch (error) {
        showActionMessage('Error stopping DDoSPot Honeypot: ' + error.message);
    }
}

// Splunk Functions
async function checkSplunkStatus() {
    try {
        const response = await makeRequest('/splunk/status');
        updateStatusSplunk('splunk-status', 'splunk-installed', 'splunk-token', 'splunk-creds', response.running, response.installed, response.token, response.creds, response.user, response.password);
        if (response.installed) {
            document.getElementById('splunk-custom-path').value = response.splunk_path || '';
        }
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
            showActionMessage('Splunk SIEM started successfully. Listening on port 8000 for web interface.');
            updateStatusSplunk('splunk-status', 'splunk-installed', 'splunk-token', 'splunk-creds', statusResponse.running, statusResponse.installed, statusResponse.token, statusResponse.creds, statusResponse.user, statusResponse.password);
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
            showActionMessage('Splunk SIEM stopped successfully.');
            updateStatusSplunk('splunk-status', 'splunk-installed', 'splunk-token', 'splunk-creds', statusResponse.running, statusResponse.installed, statusResponse.token, statusResponse.creds, statusResponse.user, statusResponse.password);
        }
    } catch (error) {
        showActionMessage('Error stopping Splunk SIEM: ' + error.message);
    }
}

async function setSplunkUser() {
    const user = document.getElementById('splunk-user').value;
    if (!user) {
        showActionMessage('Please enter a valid username for Splunk.');
        return;
    }
    try {
        const response = await makeRequest('/splunk/set-user', 'POST', { username: user });
        if (response.success) {
            showActionMessage('Splunk username set successfully.');
            document.getElementById('set-splunk-user-btn').disabled = true;
            document.getElementById('set-splunk-user-btn').classList.add('disabled');
        } else {
            showActionMessage('Error setting Splunk username. Please try again.');
        }
        const statusResponse = await makeRequest('/splunk/status');
        updateStatusSplunk('splunk-status', 'splunk-installed', 'splunk-token', 'splunk-creds', statusResponse.running, statusResponse.installed, statusResponse.token, statusResponse.creds, statusResponse.user, statusResponse.password);
    } catch (error) {
        showActionMessage('Error setting Splunk username: ' + error.message);
    }
}

async function setSplunkPassword() {
    const password = document.getElementById('splunk-password').value;
    if (!password) {
        showActionMessage('Please enter a valid password for Splunk.');
        return;
    }
    try {
        const response = await makeRequest('/splunk/set-password', 'POST', { password: password });
        if (response.success) {
            showActionMessage('Splunk password set successfully.');
            document.getElementById('set-splunk-password-btn').disabled = true;
            document.getElementById('set-splunk-password-btn').classList.add('disabled');
        } else {
            showActionMessage('Error setting Splunk password. Please try again.');
        }
        const statusResponse = await makeRequest('/splunk/status');
        updateStatusSplunk('splunk-status', 'splunk-installed', 'splunk-token', 'splunk-creds', statusResponse.running, statusResponse.installed, statusResponse.token, statusResponse.creds, statusResponse.user, statusResponse.password);
    } catch (error) {
        showActionMessage('Error setting Splunk password: ' + error.message);
    }
}

async function createSplunkToken() {
    try {
        const response = await makeRequest('/splunk/create', 'POST');
        if (response.token) {
            showActionMessage('Splunk HEC token created successfully. Token: ' + response.token);
            showActionMessage('Make sure to enable HEC tokens in Splunk Settings!')
        } else {
            showActionMessage('Error creating Splunk HEC token. Please try again.');
        }
        const statusResponse = await makeRequest('/splunk/status');
        updateStatusSplunk('splunk-status', 'splunk-installed', 'splunk-token', 'splunk-creds', statusResponse.running, statusResponse.installed, statusResponse.token, statusResponse.creds, statusResponse.user, statusResponse.password);
    } catch (error) {
        showActionMessage('Error creating Splunk HEC token: ' + error.message);
    }
}

// Suricata Functions
async function checkSuricataStatus() {
    try {
        const response = await makeRequest('/suricata/status');
        updateStatusUI('suricata-status', 'suricata-installed', null, response.running, response.installed, null, 'suricata-start-btn', 'suricata-stop-btn', null, null);
        if (response.installed) {
            document.getElementById('suricata-custom-path').value = response.suricata_path || '';
            document.getElementById('suricata-log-path').value = response.log_path || '';
        }
    } catch (error) {
        showActionMessage('Error checking Suricata IDS status: ' + error.message);
    }
}

async function setCustomLogPath() {
    const path = document.getElementById('suricata-log-path').value;
    if (!path) {
        showActionMessage('Please enter a valid path for Suricata logs.');
        return;
    }
    try {
        const response = await makeRequest('/suricata/set-log-path', 'POST', { path: path});
        if (response.success) {
            showActionMessage('Custom log path for Suricata set successfully.');
            document.getElementById('set-suricata-log-path-btn').disabled = true;
            document.getElementById('set-suricata-log-path-btn').classList.add('disabled');
        } else {
            showActionMessage(path + ' is not a valid path for Suricata logs. Please enter a valid path.');
        }
        const statusResponse = await makeRequest('/suricata/status');
        updateStatusUI('suricata-status', 'suricata-installed', null, statusResponse.running, statusResponse.installed, null, 'suricata-start-btn', 'suricata-stop-btn', null, null);
    } catch (error) {
        showActionMessage('Error setting custom log path for Suricata: ' + error.message);
    }
}

async function startSuricata() {
    try {
        showActionMessage('Starting Suricata IDS...');
        const response = await makeRequest('/suricata/start', 'POST');
        const statusResponse = await makeRequest('/suricata/status');
        if (response.success) {
            showActionMessage('Suricata IDS started successfully. Monitoring network traffic...');
            updateStatusUI('suricata-status', 'suricata-installed', null, statusResponse.running, statusResponse.installed, null, 'suricata-start-btn', 'suricata-stop-btn', null, null);
        }
    } catch (error) {
        showActionMessage('Error starting Suricata IDS: ' + error.message);
    }
}

async function stopSuricata() {
    try {
        showActionMessage('Stopping Suricata IDS...');
        const response = await makeRequest('/suricata/stop', 'POST');
        const statusResponse = await makeRequest('/suricata/status');
        if (response.success) {
            showActionMessage('Suricata IDS stopped successfully.');
            updateStatusUI('suricata-status', 'suricata-installed', null, statusResponse.running, statusResponse.installed, null, 'suricata-start-btn', 'suricata-stop-btn', null, null);
        }
    } catch (error) {
        showActionMessage('Error stopping Suricata IDS: ' + error.message);
    }
}

// Auto-refresh status on page load
window.addEventListener('DOMContentLoaded', () => {
    checkCowrieStatus();
    checkDionaeaStatus();
    checkDDoSPotStatus();
    checkSplunkStatus();
    checkSuricataStatus();
});
