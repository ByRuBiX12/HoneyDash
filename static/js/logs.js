// API URL - using relative path to work from any IP
const API_URL = '/api';

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

function toggleQueryFilter(contentId, toggleId) {
    const content = document.getElementById(contentId);
    const toggle = document.getElementById(toggleId);
    if (content.style.display === 'none') {
        content.style.display = 'block';
        toggle.style.transform = 'rotate(0deg)';
    } else {
        content.style.display = 'none';
        toggle.style.transform = 'rotate(-90deg)';
    }
}

// Toggle para campos visibles
function toggleFieldFilter(contentId, toggleId) {
    const content = document.getElementById(contentId);
    const toggle = document.getElementById(toggleId);
    if (content.style.display === 'none') {
        content.style.display = 'block';
        toggle.style.transform = 'rotate(0deg)';
    } else {
        content.style.display = 'none';
        toggle.style.transform = 'rotate(-90deg)';
    }
}

// Seleccionar todos los campos
function selectAllFields(service) {
    const checkboxes = document.querySelectorAll(`[id^="${service}-field-"]`);
    checkboxes.forEach(cb => cb.checked = true);
}

// Deseleccionar todos los campos
function deselectAllFields(service) {
    const checkboxes = document.querySelectorAll(`[id^="${service}-field-"]`);
    checkboxes.forEach(cb => cb.checked = false);
}

async function getLogs(service) {
    showActionMessage('Buscando logs...');
    const logsBox = document.getElementById(`${service}-logs`);

    if (service === 'cowrie') {
        try {
            const limit = document.getElementById('log-limit').value || 50;
            const eventid = document.getElementById('log-eventid').value || '';
            const timestampInput = document.getElementById('log-timestamp').value;

            let url = `${API_URL}/cowrie/logs?limit=${limit}`;
            if (eventid) {
                url += `&event_id=${eventid}`;
            }
            if (timestampInput) {
                url += `&timestamp=${timestampInput}`;
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
    } else if (service === 'dionaea') {
        try {
            const limit = document.getElementById('log-limit-dionaea').value || 50;
            const type = document.getElementById('log-type-dionaea').value;
            const timestampInput = document.getElementById('log-timestamp-dionaea').value;

            let url = `${API_URL}/dionaea/logs?limit=${limit}&type=${type}`

            if (timestampInput) {
                url += `&timestamp=${timestampInput}`;
            }

            const response = await fetch(url);
            const data = await response.json();

            if (data.success) {
                const statusResponse = await makeRequest('/splunk/status');
                if (statusResponse.installed && statusResponse.installed && statusResponse.token) {
                    document.getElementById('sendToSplunkDionaea').disabled = false;
                    document.getElementById('sendToSplunkDionaea').classList.remove('disabled');
                }
                const filterOption = document.getElementById('log-type-dionaea').value;
                let filteredLogs = [];
                if (filterOption === 'httpd') {
                    filteredLogs = filterDionaeaHttpLogFields(data.logs);
                } else if (filterOption === 'ftpd') {
                    filteredLogs = filterDionaeaFtpLogFields(data.logs);
                } else if (filterOption === 'mysqld') {
                    filteredLogs = filterDionaeaMySqlLogFields(data.logs);
                }

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
                document.getElementById('sendToSplunkDionaea').disabled = true;
                document.getElementById('sendToSplunkDionaea').classList.add('disabled');
                showActionMessage(`Error: ${data.error}`);
            }
        }
        catch (error) {
            logsBox.textContent = JSON.stringify({ error: error.message }, null, 2);
            document.getElementById('sendToSplunkDionaea').disabled = true;
            document.getElementById('sendToSplunkDionaea').classList.add('disabled');
            showActionMessage(`Error: ${error.message}`);
        }
    }
}

// Filter Cowrie log fields based on checkbox selection
function filterLogFields(logs) {
    const fields = ['eventid', 'timestamp', 'src_ip', 'src_port', 'username', 'password', 'duration', 'message'];
    const selectedFields = [];
    for (let i = 0; i < fields.length; i++) {
        const field = fields[i];
        const checkbox = document.getElementById(`cowrie-field-${field}`);
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

// Filter Dionaea HTTP log fields based on checkbox selection
function filterDionaeaHttpLogFields(logs) {
    const fields = ['user_agent', 'timestamp', 'src_ip', 'request_type', 'endpoint', 'username', 'password', 'filename'];
    const selectedFields = [];
    for (let i = 0; i < fields.length; i++) {
        const field = fields[i];
        const checkbox = document.getElementById(`dionaea-field-${field}`);
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

// Filter Dionaea FTP log fields based on checkbox selection
function filterDionaeaFtpLogFields(logs) {
    const fields = ['username', 'password', 'src_ip', 'filename', 'timestamp'];
    const selectedFields = [];
    for (let i = 0; i < fields.length; i++) {
        const field = fields[i];
        const checkbox = document.getElementById(`dionaea-field-${field}-ftp`);
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

// Filter Dionaea MySQL log fields based on checkbox selection
function filterDionaeaMySqlLogFields(logs) {
    const fields = ['username', 'password', 'src_ip', 'timestamp'];
    const selectedFields = [];
    for (let i = 0; i < fields.length; i++) {
        const field = fields[i];
        const checkbox = document.getElementById(`dionaea-field-${field}-mysql`);
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

// Toggle Dionaea filter options based on log type
function toggleDionaeaFilter() {
    const logType = document.getElementById('log-type-dionaea').value;
    if (logType === 'httpd') {
        document.getElementById('http-filter').style.display = 'grid';
        document.getElementById('ftp-filter').style.display = 'none';
        document.getElementById('mysql-filter').style.display = 'none';
    } else if (logType === 'ftpd') {
        document.getElementById('http-filter').style.display = 'none';
        document.getElementById('ftp-filter').style.display = 'grid';
        document.getElementById('mysql-filter').style.display = 'none';
    } else if (logType === 'mysqld') {
        document.getElementById('http-filter').style.display = 'none';
        document.getElementById('ftp-filter').style.display = 'none';
        document.getElementById('mysql-filter').style.display = 'grid';
    }
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