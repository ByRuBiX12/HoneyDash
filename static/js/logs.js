// API URL
const API_URL = 'http://localhost:5000/api';

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

        const response = await fetch(`${API_URL}${endpoint}`, options);
        const data = await response.json();

        return data;
    } catch (error) {
        showActionMessage(`Error: ${error.message}`);
        return null;
    }
}

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

function toggleQueryFilter() {
    const content = document.getElementById('query-filter-content');
    const toggle = document.getElementById('query-filter-toggle');
    if (content.style.display === 'none') {
        content.style.display = 'block';
        toggle.style.transform = 'rotate(0deg)';
    } else {
        content.style.display = 'none';
        toggle.style.transform = 'rotate(-90deg)';
    }
}

// Toggle para campos visibles
function toggleFieldFilter() {
    const content = document.getElementById('field-filter-content');
    const toggle = document.getElementById('field-filter-toggle');
    if (content.style.display === 'none') {
        content.style.display = 'block';
        toggle.style.transform = 'rotate(0deg)';
    } else {
        content.style.display = 'none';
        toggle.style.transform = 'rotate(-90deg)';
    }
}

// Seleccionar todos los campos
function selectAllFields() {
    const checkboxes = document.querySelectorAll('[id^="field-"]');
    checkboxes.forEach(cb => cb.checked = true);
}

// Deseleccionar todos los campos
function deselectAllFields() {
    const checkboxes = document.querySelectorAll('[id^="field-"]');
    checkboxes.forEach(cb => cb.checked = false);
}

async function getLogs(service) {
    showActionMessage('Buscando logs...');
    const logsBox = document.getElementById(`${service}-logs`);

    try {
        const limit = document.getElementById('log-limit').value || 50;
        const eventid = document.getElementById('log-eventid').value || '';
        const timestampInput = document.getElementById('log-timestamp').value;
        
        // Add seconds and timezone
        let timestamp = '';
        if (timestampInput) {
            timestamp = timestampInput + ':00Z';
        }

        let url = `${API_URL}/cowrie/logs?limit=${limit}`;
        if (eventid) {
            url += `&event_id=${eventid}`;
        }
        if (timestamp) {
            url += `&timestamp=${timestamp}`;
        }

        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            const statusResponse = await makeRequest('/splunk/status');
            if (statusResponse.installed && statusResponse.installed && statusResponse.token) {
                document.getElementById('sendToSplunk').disabled = false;
                document.getElementById('sendToSplunk').classList.remove('disabled');
            }
            const filteredLogs = filterLogFields(data.logs);
            
            let output = `Total de logs encontrados: ${data.logs.length}\n`;
            output += '='.repeat(80) + '\n\n';
            
            filteredLogs.forEach((log, index) => {
                output += `--- Log ${index + 1} ---\n`;
                for (const [key, value] of Object.entries(log)) {
                    output += `${key}: ${value}\n`;
                }
                output += '\n';
            });
            
            logsBox.textContent = output;
            showActionMessage(`${data.logs.length} logs encontrados`);
        } else {
            logsBox.textContent = JSON.stringify({ error: data.error }, null, 2);
            document.getElementById('sendToSplunk').disabled = true;
            document.getElementById('sendToSplunk').classList.add('disabled');
            showActionMessage(`Error: ${data.error}`);
        }
    } catch (error) {
        logsBox.textContent = JSON.stringify({ error: error.message }, null, 2);
        document.getElementById('sendToSplunk').disabled = true;
        document.getElementById('sendToSplunk').classList.add('disabled');
        showActionMessage(`Error: ${error.message}`);
    }
}

// Filter log fields based on checkbox selection
function filterLogFields(logs) {
    const fields = ['eventid', 'timestamp', 'src_ip', 'src_port', 'username', 'password', 'duration', 'message'];
    const selectedFields = [];
    for (let i = 0; i < fields.length; i++) {
        const field = fields[i];
        const checkbox = document.getElementById(`field-${field}`);
        if (checkbox && checkbox.checked) {
            selectedFields.push(field);
        }
    }

    const filteredLogs = [];
    for (let i = 0; i < logs.length; i++) {
        const log = logs[i];
        const filteredLog = {};  
        for (let j = 0; j < selectedFields.length; j++) {
            const field = selectedFields[j];
            if (log.hasOwnProperty(field)) {
                filteredLog[field] = log[field];
            }
        }
        filteredLogs.push(filteredLog);
    }
    
    return filteredLogs;
}

// POST: Enviar logs a Splunk
async function sendToSplunk(service) {
    const logsBox = document.getElementById(`${service}-logs`).textContent;

    try {
        const logsData = JSON.parse(logsBox);
        
        if (!logsData.logs || logsData.logs.length === 0) {
            showActionMessage('No logs detected to send to Splunk.');
            return;
        }

        const payload = {
            logs: logsData.logs
        };

        const response = await makeRequest('/api/splunk/send', 'POST', payload);
    }
    catch (error) {
        showActionMessage('No valid logs to send to Splunk.');
        console.error('Error:', error);
        return;
    }
}