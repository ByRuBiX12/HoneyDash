# HoneyDash
## TFG Ingeniería Informática - UDC
## Computer Engineering Final Project - UDC (Spain)

**HoneyDash** HoneyDash is more than my Final Degree Project, is the first platform ever made that simplifies and unifies several Honeypots, offering a simple way to deploy, configure and manage them through its single Dashboard.

> **Active Development**: This project is under development as part of my final degree project. Many features are still being implemented.

## Current Features

### Cowrie Honeypot Management
- **Auto-detection**: Automatically finds Cowrie installations across the system
- **Easy installation**: One-click automated setup with all dependencies
- **SSH redirection**: Moves real SSH to a random port (1024-65535) and redirects port 22 to Cowrie
- **Port configuration**: Configures Cowrie to listen on port 2222
- **iptables management**: Handles NAT rules automatically
- **Start/Stop control**: Simple honeypot lifecycle management
- **Auto-cleanup**: Restores SSH and iptables on exit (via SIGINT handler)
- **Security**: Cowrie runs as non-root user (drops privileges at runtime)

### REST API
- Full CRUD operations for honeypot management
- JSON responses with detailed status information
- CORS-enabled for frontend integration

### Web Dashboard
- Real-time status monitoring (auto-refresh)
- One-click operations for all endpoints
- JSON response viewer with syntax highlighting
- Responsive design with gradient UI

## Quick Start

### Prerequisites
- **OS**: Linux (Debian/Ubuntu/Kali)
- **Python**: 3.8+
- **Privileges**: Must run with `sudo` from a non-root user

### Installation

```bash
# Clone repository
git clone <your-repo> HoneyDash
cd HoneyDash

# Install dependencies
pip install -r requirements.txt

# Run (IMPORTANT: use sudo from non-root user)
sudo python3 app.py
```

Access the dashboard at: `http://localhost:5000`

## API Reference

### Status
```bash
GET /api/cowrie/status
```

### Operations
```bash
POST /api/cowrie/install      # Install Cowrie
POST /api/cowrie/configure    # Configure port 2222
POST /api/cowrie/setup-redirect  # Move SSH + add iptables rule
POST /api/cowrie/start        # Start honeypot (runs as non-root)
POST /api/cowrie/stop         # Stop honeypot
POST /api/cowrie/cleanup      # Restore SSH to port 22
```

### Manual Path (if auto-detection fails)
```bash
POST /api/cowrie/set-path
Content-Type: application/json

{"path": "/custom/path/to/cowrie"}
```

## Security Model

- **Application**: Must run with `sudo` from a non-root user
- **Cowrie process**: Automatically drops privileges using `sudo -u $SUDO_USER`
- **SSH protection**: Real SSH moved to random port, accessible only to authorized users
- **Auto-cleanup**: SIGINT handler restores original configuration on exit

## Project Structure

```
HoneyDash/
├── app.py                    # Flask backend with signal handling
├── honeypots/
│   └── cowrie_manager.py    # Cowrie lifecycle management
├── static/
│   └── index.html           # Web dashboard
└── requirements.txt         # Python dependencies
```

## Roadmap

- [X] Cowrie honeypot
- [ ] Dionaea honeypot
- [ ] DDoSPot honeypot
- [ ] Real-time log parsing and visualization
- [ ] Splunk HEC integration
- [ ] Suricata alerts analysis with CVE lookup
- [ ] Advanced dashboard with metrics
- [ ] Docker deployment

## Troubleshooting

**"Must run with sudo"**: Execute as `sudo python3 app.py` from your regular user (not root)

**Auto-detection fails**: Use `/api/cowrie/set-path` endpoint to set Cowrie location manually

**Lost SSH access**: SSH moved to random port shown in `/api/cowrie/setup-redirect` response. Run `/api/cowrie/cleanup` to restore port 22.

## License

[To be defined]

---

**Author**: Rubén Barba Paz  
**Institution**: Universidad de La Coruña (UDC), Spain
