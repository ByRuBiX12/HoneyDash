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
    const logsBoxHidden = document.getElementById(`${service}-logs-hidden`);
    const logsContainer = document.getElementById(`${service}-logs-container`);

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
                let outputHidden = JSON.stringify(filteredLogs);

                filteredLogs.forEach((log, index) => {
                    output += `--- Log ${index + 1} ---\n`;
                    for (const [key, value] of Object.entries(log)) {
                        output += `${key}: ${value}\n`;
                    }
                    output += '\n';
                });

                logsContainer.style.display = 'block';
                logsBox.textContent = output;
                logsBoxHidden.textContent = outputHidden;
                showActionMessage(`${data.logs.length} logs encontrados`);
            } else {
                logsContainer.style.display = 'none';
                logsBox.textContent = JSON.stringify({ error: data.error }, null, 2);
                document.getElementById('sendToSplunk').disabled = true;
                document.getElementById('sendToSplunk').classList.add('disabled');
                showActionMessage(`Error: ${data.error}`);
            }
        } catch (error) {
            logsContainer.style.display = 'none';
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
                let filteredLogs = [];
                if (type === 'httpd') {
                    filteredLogs = filterDionaeaHttpLogFields(data.logs);
                } else if (type === 'ftpd') {
                    filteredLogs = filterDionaeaFtpLogFields(data.logs);
                } else if (type === 'mysqld') {
                    filteredLogs = filterDionaeaMySqlLogFields(data.logs);
                }

                let output = `Total de logs encontrados: ${data.logs.length}\n`;
                output += '='.repeat(80) + '\n\n';
                let outputHidden = JSON.stringify(filteredLogs);

                filteredLogs.forEach((log, index) => {
                    output += `--- Log ${index + 1} ---\n`;
                    for (const [key, value] of Object.entries(log)) {
                        output += `${key}: ${value}\n`;
                    }
                    output += '\n';
                });

                logsContainer.style.display = 'block';
                logsBox.textContent = output;
                logsBoxHidden.textContent = outputHidden;
                showActionMessage(`${data.logs.length} logs encontrados`);
            } else {
                logsContainer.style.display = 'none';
                logsBox.textContent = JSON.stringify({ error: data.error }, null, 2);
                document.getElementById('sendToSplunkDionaea').disabled = true;
                document.getElementById('sendToSplunkDionaea').classList.add('disabled');
                showActionMessage(`Error: ${data.error}`);
            }
        }
        catch (error) {
            logsContainer.style.display = 'none';
            logsBox.textContent = JSON.stringify({ error: error.message }, null, 2);
            document.getElementById('sendToSplunkDionaea').disabled = true;
            document.getElementById('sendToSplunkDionaea').classList.add('disabled');
            showActionMessage(`Error: ${error.message}`);
        }
    } else if (service === 'ddospot') {
        try {
            const limit = document.getElementById('log-limit-ddospot').value || 50;
            const protocol = document.getElementById('log-protocol-ddospot').value;
            const timestampInput = document.getElementById('log-timestamp-ddospot').value;

            let url = `${API_URL}/ddospot/logs?limit=${limit}&protocol=${protocol}`

            if (timestampInput) {
                url += `&timestamp=${timestampInput}`;
            }

            const response = await fetch(url);
            const data = await response.json();

            if (data.success) {
                const statusResponse = await makeRequest('/splunk/status');
                if (statusResponse.installed && statusResponse.installed && statusResponse.token) {
                    document.getElementById('sendToSplunkDdospot').disabled = false;
                    document.getElementById('sendToSplunkDdospot').classList.remove('disabled');
                }
                let filteredLogs = [];
                if (protocol === 'dnspot') {
                    filteredLogs = filterDdospotDnsLogFields(data.logs);
                } else if (protocol === 'ntpot') {
                    filteredLogs = filterDdospotNtpLogFields(data.logs);
                } else if (protocol === 'genericpot') {
                    filteredLogs = filterDdospotSnmpLogFields(data.logs);
                } else if (protocol === 'ssdpot') {
                    filteredLogs = filterDdospotSsdpLogFields(data.logs);
                } else if (protocol === 'chargenpot') {
                    filteredLogs = filterDdospotChargenLogFields(data.logs);
                }

                let output = `Total de logs encontrados: ${data.logs.length}\n`;
                output += '='.repeat(80) + '\n\n';
                let outputHidden = JSON.stringify(filteredLogs);

                filteredLogs.forEach((log, index) => {
                    output += `--- Log ${index + 1} ---\n`;
                    for (const [key, value] of Object.entries(log)) {
                        output += `${key}: ${value}\n`;
                    }
                    output += '\n';
                });

                logsContainer.style.display = 'block';
                logsBox.textContent = output;
                logsBoxHidden.textContent = outputHidden;
                showActionMessage(`${data.logs.length} logs encontrados`);
            } else {
                logsContainer.style.display = 'none';
                logsBox.textContent = JSON.stringify({ error: data.error }, null, 2);
                document.getElementById('sendToSplunkDdospot').disabled = true;
                document.getElementById('sendToSplunkDdospot').classList.add('disabled');
                showActionMessage(`Error: ${data.error}`);
            }
        }
        catch (error) {
            logsContainer.style.display = 'none';
            logsBox.textContent = JSON.stringify({ error: error.message }, null, 2);
            document.getElementById('sendToSplunkDdospot').disabled = true;
            document.getElementById('sendToSplunkDdospot').classList.add('disabled');
            showActionMessage(`Error: ${error.message}`);
        }
        }
}

// Filter Cowrie log fields based on checkbox selection
function filterLogFields(logs) {
    const fields = ['honeypot', 'eventid', 'timestamp', 'src_ip', 'src_port', 'username', 'password', 'duration', 'message'];
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
    const fields = ['honeypot', 'type', 'user_agent', 'timestamp', 'src_ip', 'request_type', 'endpoint', 'username', 'password', 'filename'];
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
    const fields = ['honeypot', 'type', 'username', 'password', 'src_ip', 'filename', 'timestamp'];
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
    const fields = ['honeypot', 'type', 'username', 'password', 'src_ip', 'timestamp'];
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

// Filter DDoSPot DNS log fields based on checkbox selection
function filterDdospotDnsLogFields(logs) {
    const fields = ['honeypot', 'protocol', 'src_ip', 'src_port', 'domain_name', 'dns_type', 'attack_start', 'attack_end', 'packet_count', 'amplification_factor', 'severity'];
    const selectedFields = [];
    for (let i = 0; i < fields.length; i++) {
        const field = fields[i];
        const checkbox = document.getElementById(`ddospot-field-${field}-dns`);
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

// Filter DDoSPot NTP log fields based on checkbox selection
function filterDdospotNtpLogFields(logs) {
    const fields = ['honeypot', 'protocol', 'src_ip', 'src_port', 'mode', 'attack_start', 'attack_end', 'packet_count', 'amplification_factor', 'severity'];
    const selectedFields = [];
    for (let i = 0; i < fields.length; i++) {
        const field = fields[i];
        const checkbox = document.getElementById(`ddospot-field-${field}-ntp`);
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

// Filter DDoSPot SNMP log fields based on checkbox selection
function filterDdospotSnmpLogFields(logs) {
    const fields = ['honeypot', 'protocol', 'src_ip', 'src_port', 'dst_port', 'attack_start', 'attack_end', 'packet_count', 'amplification_factor', 'severity'];
    const selectedFields = [];
    for (let i = 0; i < fields.length; i++) {
        const field = fields[i];
        const checkbox = document.getElementById(`ddospot-field-${field}-snmp`);
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

// Filter DDoSPot SSDP log fields based on checkbox selection
function filterDdospotSsdpLogFields(logs) {
    const fields = ['honeypot', 'protocol', 'src_ip', 'src_port', 'st', 'mx', 'attack_start', 'attack_end', 'packet_count', 'amplification_factor', 'severity'];
    const selectedFields = [];
    for (let i = 0; i < fields.length; i++) {
        const field = fields[i];
        const checkbox = document.getElementById(`ddospot-field-${field}-ssdp`);
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

// Filter DDoSPot CHARGEN log fields based on checkbox selection
function filterDdospotChargenLogFields(logs) {
    const fields = ['honeypot', 'protocol', 'src_ip', 'src_port', 'attack_start', 'attack_end', 'packet_count', 'amplification_factor', 'severity'];
    const selectedFields = [];
    for (let i = 0; i < fields.length; i++) {
        const field = fields[i];
        const checkbox = document.getElementById(`ddospot-field-${field}-chargen`);
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

// Toggle DDoSPot filter options based on log type
function toggleDdospotFilter() {
    const protocol = document.getElementById('log-protocol-ddospot').value;
    if (protocol === 'dnspot') {
        document.getElementById('dns-filter').style.display = 'grid';
        document.getElementById('ntp-filter').style.display = 'none';
        document.getElementById('snmp-filter').style.display = 'none';
        document.getElementById('ssdp-filter').style.display = 'none';
        document.getElementById('chargen-filter').style.display = 'none';
    } else if (protocol === 'ntpot') {
        document.getElementById('dns-filter').style.display = 'none';
        document.getElementById('ntp-filter').style.display = 'grid';
        document.getElementById('snmp-filter').style.display = 'none';
        document.getElementById('ssdp-filter').style.display = 'none';
        document.getElementById('chargen-filter').style.display = 'none';
    } else if (protocol === 'genericpot') {
        document.getElementById('dns-filter').style.display = 'none';
        document.getElementById('ntp-filter').style.display = 'none';
        document.getElementById('snmp-filter').style.display = 'grid';
        document.getElementById('ssdp-filter').style.display = 'none';
        document.getElementById('chargen-filter').style.display = 'none';
    } else if (protocol === 'ssdpot') {
        document.getElementById('dns-filter').style.display = 'none';
        document.getElementById('ntp-filter').style.display = 'none';
        document.getElementById('snmp-filter').style.display = 'none';
        document.getElementById('ssdp-filter').style.display = 'grid';
        document.getElementById('chargen-filter').style.display = 'none';
    } else if (protocol === 'chargenpot') {
        document.getElementById('dns-filter').style.display = 'none';
        document.getElementById('ntp-filter').style.display = 'none';
        document.getElementById('snmp-filter').style.display = 'none';
        document.getElementById('ssdp-filter').style.display = 'none';
        document.getElementById('chargen-filter').style.display = 'grid';
    }
}

// POST: Enviar logs a Splunk
async function sendToSplunk(service) {
    const logsBox = document.getElementById(`${service}-logs-hidden`).textContent;

    try {
        const logsData = JSON.parse(logsBox);

        const payload = {
            logs: logsData
        };

        const response = await makeRequest('/splunk/send', 'POST', payload);
        if (response.success) {
            showActionMessage(`${service} logs succesfully sent to Splunk`);
        }
    }
    catch (error) {
        showActionMessage('No valid logs to send to Splunk.');
        console.error('Error:', error);
        return;
    }
}

// GET: Get Dionaea binaries information and show them in cards
async function getBinaries() {
    try {
        let currentCursor = 1;
        
        const loadPage = async (page) => {
            const response = await makeRequest(`/dionaea/binaries?page=${page}`);
            
            const binariesContainer = document.getElementById('binaries-container');
            binariesContainer.innerHTML = '';
            binariesContainer.style.marginBottom = '1rem';

            if (response.binaries.length === 0) {
                binariesContainer.innerHTML = '<p style="color: #bdc3c7; text-align: center; grid-column: 1 / -1;">No binaries found.</p>';
                return;
            }
            
            const leftArrow = document.createElement('a');
            leftArrow.className = 'pagination-arrow';
            leftArrow.innerHTML = '&#9668; Previous';
            if (currentCursor === 1) {
                leftArrow.classList.add('pagination-arrow-disabled');
            }
            leftArrow.onclick = async () => {
                if (currentCursor > 1) {
                    currentCursor--;
                    await loadPage(currentCursor);
                }
            };
            binariesContainer.appendChild(leftArrow);
            
            const rightArrow = document.createElement('a');
            rightArrow.className = 'pagination-arrow';
            rightArrow.innerHTML = 'Next &#9658;';
            if (currentCursor >= response.total_pages) {
                rightArrow.classList.add('pagination-arrow-disabled');
            }
            rightArrow.onclick = async () => {
                if (currentCursor < response.total_pages) {
                    currentCursor++;
                    await loadPage(currentCursor);
                }
            };
            binariesContainer.appendChild(rightArrow);

            printBinaries(response);
        };
        
        await loadPage(currentCursor);
        
    } catch (error) {
        showActionMessage(`Error: ${error.message}`);
    }
}

async function printBinaries(response) {
    try {
        response.binaries.forEach(binary => {
                const binaryCard = document.createElement('div');
                binaryCard.className = 'binary';

                const md5Hash = document.createElement('p');
                md5Hash.innerHTML = `<strong>MD5 Hash:</strong> <span style="font-family: 'Courier New', monospace; font-size: 0.85rem; word-break: break-all;">${binary.md5hash}</span>`;
                binaryCard.appendChild(md5Hash);

                const size = document.createElement('p');
                const sizeInKB = (binary.size / 1024).toFixed(2);
                size.innerHTML = `<strong>Size:</strong> <span>${binary.size} bytes (${sizeInKB} KB)</span>`;
                binaryCard.appendChild(size);

                const timestamp = document.createElement('p');
                timestamp.innerHTML = `<strong>Timestamp:</strong> <span>${binary.timestamp}</span>`;
                binaryCard.appendChild(timestamp);

                const searchLink = document.createElement('a');
                searchLink.href = `https://www.virustotal.com/gui/search/${binary.md5hash}`;
                searchLink.target = '_blank';
                searchLink.classList.add('search-link');
                searchLink.title = 'Search on VirusTotal';

                const searchIcon = document.createElement('a');
                searchIcon.className = 'search-icon';
                searchIcon.innerHTML = 'Analyze &#x2315;';
                
                searchLink.appendChild(searchIcon);
                binaryCard.appendChild(searchLink);
                document.getElementById('binaries-container').appendChild(binaryCard);
            });
            
            showActionMessage(`Successfully loaded ${response.binaries.length} binaries`);
    } catch (error) {
        showActionMessage(`Error displaying binaries: ${error.message}`);
    }
}

// GET: Get Suricata Alerts information and show them in cards
async function getAlerts() {
    try {
        let currentCursor = 0;
        const severity = document.getElementById('log-severity-suricata').value;
        const protocol = document.getElementById('log-protocol-suricata').value;
        const timestampFrom = document.getElementById('log-timestamp_from-suricata').value;
        const timestampTo = document.getElementById('log-timestamp_to-suricata').value;
        
        const loadPage = async (cursor) => {
            const response = await makeRequest(`/suricata/alerts?severity=${severity}&protocol=${protocol}&timestamp_from=${timestampFrom}&timestamp_to=${timestampTo}&cursor_next=${cursor}`);
            
            const alertsContainer = document.getElementById('alerts-container');
            alertsContainer.innerHTML = '';
            alertsContainer.style.marginBottom = '1rem';

            if (response.alerts.length === 0) {
                alertsContainer.innerHTML = '<p style="color: #bdc3c7; text-align: center; grid-column: 1 / -1;">No alerts found.</p>';
                return;
            }
            
            const leftArrow = document.createElement('a');
            leftArrow.className = 'pagination-arrow';
            leftArrow.innerHTML = '&#9668; Previous';
            if (currentCursor === 0) {
                leftArrow.classList.add('pagination-arrow-disabled');
            }
            leftArrow.onclick = async () => {
                if (currentCursor > 0) {
                    currentCursor = response.cursor_prev;
                    await loadPage(currentCursor);
                }
            };
            alertsContainer.appendChild(leftArrow);
            
            const rightArrow = document.createElement('a');
            rightArrow.className = 'pagination-arrow';
            rightArrow.innerHTML = 'Next &#9658;';
            if (response.has_next === false) {
                rightArrow.classList.add('pagination-arrow-disabled');
            }
            
            rightArrow.onclick = async () => {
                if (response.has_next === true) {
                    currentCursor = response.cursor_next;
                    await loadPage(currentCursor);
                }
            };

            alertsContainer.appendChild(rightArrow);
            printAlerts(response);
        };
        
        await loadPage(currentCursor);
        
    } catch (error) {
        showActionMessage(`Error: ${error.message}`);
    }
}

async function printAlerts(response) {
    try {
        response.alerts.forEach(alert => {
                const alertCard = document.createElement('div');
                if (alert.severity === 1) {
                    alertCard.className = 'alert alert-critical';
                } else if (alert.severity === 2) {
                    alertCard.className = 'alert alert-high';
                } else if (alert.severity === 3) {
                    alertCard.className = 'alert alert-medium';
                } else if (alert.severity === 4) {
                    alertCard.className = 'alert alert-low';
                }
                const category = document.createElement('p');
                category.innerHTML = `<strong>${alert.category}</strong>`;
                alertCard.appendChild(category);

                const proto = document.createElement('p');
                proto.innerHTML = `<strong>Protocol:</strong> <span>${alert.protocol}</span>`;
                alertCard.appendChild(proto);

                const iface = document.createElement('p');
                iface.innerHTML = `<strong>Interface:</strong> <span>${alert.in_iface}</span>`;
                alertCard.appendChild(iface);

                if (alert.cve != 'N/A') {
                    const cve = document.createElement('p');
                    cve.innerHTML = `<strong>CVE:</strong> <span>${alert.cve}</span>`;
                    alertCard.appendChild(cve);
                }

                const timestamp = document.createElement('p');
                timestamp.innerHTML = `<strong>Timestamp:</strong> <span>${alert.timestamp}</span>`;
                alertCard.appendChild(timestamp);

                document.getElementById('alerts-container').appendChild(alertCard);
            });
            
            showActionMessage(`Successfully loaded ${response.alerts.length} alerts`);
    } catch (error) {
        showActionMessage(`Error displaying alerts: ${error.message}`);
    }
}