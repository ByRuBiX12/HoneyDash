# HoneyDash
## TFG Ingeniería Informática - UDC
## Computer Engineering Final Project - UDC (Spain)

**HoneyDash** is more than my Final Degree Project, is the first platform ever made that simplifies and unifies several Honeypots, offering a simple way to deploy, configure and manage them through its single Dashboard, as well as offering a great integration with Splunk SIEM.

> **Active Development**: This project is under development as part of my final degree project. Many features are still being implemented.

## Current Features

### Cowrie Honeypot Management
- **Auto-detection**: Automatically finds Cowrie installations across the system
- **Easy installation**: One-click automated setup with all dependencies and virtual environment
- **SSH redirection**: Moves real SSH to a random port (1024-65535) and redirects port 22 to Cowrie
- **Smart configuration**: Automatically configures Cowrie to listen on port 2222
- **iptables management**: Handles NAT rules automatically for transparent redirection
- **Lifecycle control**: Start/Stop operations with privilege management
- **Log retrieval**: Query Cowrie JSON logs with filtering by limit, event type, and timestamp
- **Auto-cleanup**: Restores SSH and iptables on exit (SIGINT handler)
- **Security**: Cowrie runs as non-root user (automatic privilege dropping)

### Dionaea Honeypot Management
- **Auto-detection**: Searches for unique Dionaea directories with prioritized /opt scanning
- **Source compilation**: Automated build from GitHub with all dependencies
- **Python 3.13 compatibility**: Automatic patching of build files to disable incompatible modules
- **One-click installation**: Handles git clone, CMake configuration, compilation, and installation
- **Multi-protocol support**: Captures attacks on SMB, HTTP, FTP, MySQL, MSSQL, and more (without libemu/python modules)
- **Status monitoring**: Real-time detection of installation and running state
- **Simplified UI**: Full-width install button with streamlined controls

### Splunk SIEM Integration
- **Status monitoring**: Check if Splunk is installed and running
- **Service control**: Start/Stop Splunk from the dashboard
- **HEC token management**: Automatic creation and retrieval of HTTP Event Collector tokens
- **Event forwarding**: Send honeypot logs to Splunk with configurable sourcetype and index
- **Batch processing**: Handles multiple events efficiently with error tracking

### REST API
- Full CRUD operations for honeypot and SIEM management
- Comprehensive error handling with descriptive messages
- JSON responses with detailed status information
- CORS-enabled for frontend integration
- Query parameters for log filtering
- Dionaea endpoints for status, installation, and control

### Web Dashboard
- Modern card-based UI with gradient design
- Navigation bar with Home and Logs sections
- Real-time status monitoring with multiple badges per service
- Organized button layouts with logical grouping
- Section dividers for Honeypots, SIEM, and IDS
- Responsive grid layout (3→2→1 columns)
- Stacked notification system with smooth slide animations
- **Logs page**: Filter and visualize Cowrie logs with field selection
- JSON response viewer with syntax highlighting
- Responsive design with gradient UI and hover animations
- Generic status update function supporting optional UI elements

## Quick Start

### Prerequisites
- **OS**: Linux (Debian/Ubuntu/Kali)
- **Python**: 3.8+
- **Privileges**: Must run with `sudo` from a non-root user

### Installation

```bash
# Clone repository
git clone https://github.com/ByRuBiX12/HoneyDash.git HoneyDash
cd HoneyDash

# Install dependencies
pip install -r requirements.txt

# Run (IMPORTANT: use sudo from non-root user)
sudo python3 app.py
```

Access the dashboard at: `http://localhost:5000`

## API Reference

### Cowrie Endpoints
```bash
# Status and configuration
GET  /api/cowrie/status
POST /api/cowrie/set-path        # Manual path: {"path": "/custom/path"}

# Installation and setup
POST /api/cowrie/install
POST /api/cowrie/configure
POST /api/cowrie/setup-redirect

# Operations
POST /api/cowrie/start
POST /api/cowrie/stop
POST /api/cowrie/cleanup

# Log retrieval
GET  /api/cowrie/logs?limit=50&event_id=cowrie.login.success&timestamp=2024-01-01T00:00:00
```

### Splunk Endpoints
```bash
# Status and control
GET  /api/splunk/status
POST /api/splunk/start
POST /api/splunk/stop

# Token management
GET  /api/splunk/search          # Find HoneyDash HEC token
POST /api/splunk/create          # Create HEC token

# Event forwarding
POST /api/splunk/send            # Body: {"logs": [{event1}, {event2}]}
```

## Security Model

- **Application**: Must run with `sudo` from a non-root user
- **Cowrie process**: Automatically drops privileges using `sudo -u $SUDO_USER`
- **SSH protection**: Real SSH moved to random port, accessible only to authorized users
- **Auto-cleanup**: SIGINT handler restores original configuration on exit

## Project Structure

```
HoneyDash/
├── app.py                    # Flask backend with API endpoints and signal handling
├── honeypots/
│   └── cowrie_manager.py    # Cowrie lifecycle and log management
├── siem/
│   └── splunk_manager.py    # Splunk integration and HEC communication
├── static/
│   ├── index.html           # Main dashboard interface
│   ├── css/
│   │   └── style.css        # Modern gradient styling with responsive design
│   ├── js/
│   │   └── dashboard.js     # Dashboard interactions and API calls
│   └── assets/              # Logo and icons
└── requirements.txt         # Python dependencies (Flask, requests, etc.)
```

## Roadmap

- [X] Cowrie honeypot integration
- [X] Splunk SIEM connectivity
- [X] Log retrieval and filtering
- [X] Modern web dashboard with responsive design
- [ ] Real-time log visualization on dashboard
- [ ] Dionaea honeypot support
- [ ] DDoSPot honeypot support
- [ ] Suricata IDS integration with CVE enrichment
- [ ] Advanced threat analytics
- [ ] Docker deployment option

## Troubleshooting

**"Must run with sudo"**: Execute as `sudo python3 app.py` from your regular user (not root)

**Cowrie auto-detection fails**: Use `/api/cowrie/set-path` endpoint with custom path

**Lost SSH access**: SSH moved to random port shown in `/api/cowrie/setup-redirect` response. Run `/api/cowrie/cleanup` to restore port 22

**Splunk token not found**: Ensure Splunk is running, then use `/api/splunk/create` to generate HEC token

**Events not sent to Splunk**: Verify HEC is enabled and token exists. Check logs contain `{"logs": [...]}`structure

## License

[To be defined]

---

**Author**: Rubén Barba Paz  
**Institution**: Universidad de La Coruña (UDC), Spain
