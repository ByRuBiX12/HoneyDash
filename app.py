from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import sys
from pathlib import Path
from signal import signal, SIGINT
import pwd

from honeypots.cowrie_manager import CowrieManager
from honeypots.dionaea_manager import DionaeaManager
from honeypots.ddospot_manager import DDoSPotManager
from siem.splunk_manager import SplunkManager
from ids.suricata_manager import SuricataManager

# Add siem and honeypots directories to path
sys.path.insert(0, str(Path(__file__).parent))


app = Flask(__name__, static_folder='static')
CORS(app)


@app.route('/')
def index():
    """Serve the HTML frontend"""
    return send_from_directory('static', 'index.html')


@app.route('/api')
def api_info():
    """API Information"""
    return jsonify({
        "name": "HoneyDash API",
        "version": "1.0.0",
        "description": "Backend for honeypot management, observability, and threat analysis",
        "endpoints": {
            "cowrie": {
                "status": "/api/cowrie/status",
                "set_path": "/api/cowrie/set-path",
                "install": "/api/cowrie/install",
                "configure": "/api/cowrie/configure",
                "setup_redirect": "/api/cowrie/setup-redirect",
                "start": "/api/cowrie/start",
                "stop": "/api/cowrie/stop",
                "cleanup": "/api/cowrie/cleanup",
                "logs": "/api/cowrie/logs?limit=50&event_id=cowrie.login.success&timestamp=2024-01-01T00:00:00"
            }
        }
    })


# ============== COWRIE ENDPOINTS ==============

@app.route('/api/cowrie/status', methods=['GET'])
def cowrie_status():
    """Gets the current status of Cowrie"""
    try:
        status = cowrie_manager.get_status()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Error getting Cowrie status"
        }), 500


@app.route('/api/cowrie/set-path', methods=['POST'])
def cowrie_set_path():
    """Manually sets Cowrie installation path"""
    try:
        data = request.get_json()
        
        if not data or 'path' not in data:
            return jsonify({
                "success": False,
                "message": "'path' field is required in JSON"
            }), 400
        
        result = cowrie_manager.set_cowrie_path(data['path'])
        status_code = 200 if result["success"] else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error setting Cowrie path"
        }), 500


@app.route('/api/cowrie/install', methods=['POST'])
def cowrie_install():
    """Installs Cowrie honeypot"""
    try:
        # Check if running as root
        if os.geteuid() != 0: # Get EFFECTIVE not real UID
            return jsonify({
                "success": False,
                "message": "Root privileges are required to install Cowrie"
            }), 403
        
        result = cowrie_manager.install()
        status_code = 200 if result["success"] else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error installing Cowrie"
        }), 500


@app.route('/api/cowrie/configure', methods=['POST'])
def cowrie_configure():
    """Configures Cowrie to listen on port 2222"""
    try:
        result = cowrie_manager.configure()
        status_code = 200 if result["success"] else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error configuring Cowrie"
        }), 500


@app.route('/api/cowrie/setup-redirect', methods=['POST'])
def cowrie_setup_redirect():
    """Configures SSH redirection and iptables rules"""
    try:
        # Check for root privileges
        if os.geteuid() != 0:
            return jsonify({
                "success": False,
                "message": "Root privileges are required to configure redirection"
            }), 403
        
        result = cowrie_manager.setup_ssh_redirect()
        status_code = 200 if result["success"] else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error configuring SSH redirection"
        }), 500


@app.route('/api/cowrie/start', methods=['POST'])
def cowrie_start():
    """Starts Cowrie"""
    try:
        result = cowrie_manager.start()
        status_code = 200 if result["success"] else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error starting Cowrie"
        }), 500


@app.route('/api/cowrie/stop', methods=['POST'])
def cowrie_stop():
    """Stops Cowrie"""
    try:
        result = cowrie_manager.stop()
        status_code = 200 if result["success"] else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error stopping Cowrie"
        }), 500


@app.route('/api/cowrie/cleanup', methods=['POST'])
def cowrie_cleanup():
    """Cleans up configuration: removes iptables rules and restores SSH"""
    try:
        # Check for root privileges
        if os.geteuid() != 0:
            return jsonify({
                "success": False,
                "message": "Root privileges are required to clean up configuration"
            }), 403
        
        result = cowrie_manager.cleanup()
        status_code = 200 if result["success"] else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error cleaning up configuration"
        }), 500

@app.route('/api/cowrie/logs', methods=['GET'])
def cowrie_logs():
    """Retrieves Cowrie logs with optional filtering"""
    try:
        limit = request.args.get('limit', default=50, type=int)
        event_id = request.args.get('event_id', default=None, type=str)
        timestamp = request.args.get('timestamp', default=None, type=str)

        result = cowrie_manager.get_logs(limit=limit, event_id=event_id, timestamp=timestamp)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error retrieving Cowrie logs"
        })
    
# ============== DIONAEA ENDPOINTS ==============
@app.route('/api/dionaea/status', methods=['GET'])
def dionaea_status():
    """Gets the current status of Dionaea"""
    try:
        status = dionaea_manager.get_status()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Error getting Dionaea status"
        }), 500

@app.route('/api/dionaea/install', methods=['POST'])
def dionaea_install():
    """Installs Dionaea honeypot"""
    try:
        # Check if running as root
        if os.geteuid() != 0: # Get EFFECTIVE not real UID
            return jsonify({
                "success": False,
                "message": "Root privileges are required to install Dionaea"
            }), 403
        
        result = dionaea_manager.install()
        status_code = 200 if result["success"] else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error installing Dionaea"
        }), 500

@app.route('/api/dionaea/start', methods=['POST'])
def dionaea_start():
    """Starts Dionaea honeypot"""
    try:
        result = dionaea_manager.start()
        status_code = 200 if result["success"] else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error starting Dionaea"
        }), 500

@app.route('/api/dionaea/stop', methods=['POST'])
def dionaea_stop():
    """Stops Dionaea honeypot"""
    try:
        result = dionaea_manager.stop()
        status_code = 200 if result["success"] else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error stopping Dionaea"
        }), 500

@app.route('/api/dionaea/logs', methods=['GET'])
def dionaea_logs():
    """Retrieves Dionaea logs"""
    try:
        limit = request.args.get('limit', default=50, type=int)
        log_type = request.args.get('type', default="httpd", type=str)
        timestamp = request.args.get('timestamp', default=None, type=str)

        result = dionaea_manager.get_logs(limit=limit, itype=log_type, timestamp=timestamp)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error retrieving Dionaea logs"
        }), 500

@app.route('/api/dionaea/binaries', methods=['GET'])
def dionaea_binaries():
    """Retrieves metadata of binaries captured by Dionaea"""
    try:
        page = request.args.get('page', default=1, type=int)
        result = dionaea_manager.get_binaries(page=page)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error retrieving Dionaea binaries"
        }), 500


# ============== DDOSPOT ENDPOINTS ==============

@app.route('/api/ddospot/status', methods=['GET'])
def ddospot_status():
    """Gets the current status of DDoSPot"""
    try:
        status = ddospot_manager.get_status()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Error getting DDoSPot status"
        }), 500

@app.route('/api/ddospot/install', methods=['POST'])
def ddospot_install():
    """Installs DDOSPot honeypot"""
    try:
        # Check if running as root
        if os.geteuid() != 0: # Get EFFECTIVE not real UID
            return jsonify({
                "success": False,
                "message": "Root privileges are required to install DDoSPot"
            }), 403
        
        result = ddospot_manager.install()
        status_code = 200 if result["success"] else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error installing DDosPot"
        }), 500

@app.route('/api/ddospot/start', methods=['POST'])
def ddospot_start():
    """Starts DDoSPot"""
    try:
        result = ddospot_manager.start()
        status_code = 200 if result["success"] else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error starting DDosPot"
        }), 500

@app.route('/api/ddospot/stop', methods=['POST'])
def ddospot_stop():
    """Stop DDoSPot"""
    try:
        result = ddospot_manager.stop()
        status_code = 200 if result["success"] else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Error stopping DDosPot"
        }), 500

@app.route('/api/ddospot/logs', methods=['GET'])
def ddospot_logs():
    """Retrieves DDoSPot logs with optional filtering"""
    try:
        limit = request.args.get('limit', default=50, type=int)
        protocol = request.args.get('protocol', default=None, type=str)
        timestamp = request.args.get('timestamp', default=None, type=str)

        result = ddospot_manager.get_logs(limit=limit, protocol=protocol, timestamp=timestamp)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error retrieving DDoSPot logs"
        }), 500

# ============== SPLUNK ENDPOINTS ==============
@app.route('/api/splunk/status', methods=['GET'])
def splunk_status():
    """Gets the current status of Splunk"""
    try:
        status = splunk_manager.get_status()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Error getting Splunk status"
        }), 500

@app.route('/api/splunk/set-path', methods=['POST'])
def splunk_set_path():
    """Manually sets Splunk installation path"""
    try:
        data = request.get_json()
        
        if not data or 'path' not in data:
            return jsonify({
                "success": False,
                "message": "'path' field is required in JSON"
            }), 400
        
        result = splunk_manager.set_splunk_path(data['path'])
        status_code = 200 if result["success"] else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error setting Splunk path"
        }), 500

@app.route('/api/splunk/start', methods=['POST'])
def splunk_start():
    """Starts Splunk"""
    try:
        result = splunk_manager.start()
        status_code = 200 if result["success"] else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Error starting Splunk"
        }), 500

@app.route('/api/splunk/stop', methods=['POST'])
def splunk_stop():
    """Stop Splunk"""
    try:
        result = splunk_manager.stop()
        status_code = 200 if result["success"] else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Error stopping Splunk"
        }), 500

@app.route('/api/splunk/search', methods=['GET'])
def splunk_search():
    """Searches for HoneyDash token in Slunk's HTTP Event Collector inputs"""
    try:
        result = splunk_manager.search_token()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Error searching for token in Splunk"
        }), 500
    
@app.route('/api/splunk/create', methods=['POST'])
def splunk_create():
    """Creates HoneyDash token in Splunk's HTTP Event Collector inputs"""
    try:
        result = splunk_manager.create_token()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Error creating token in Splunk"
        }), 500

@app.route('/api/splunk/send', methods=['POST'])
def splunk_send():
    """Sends event to Splunk using the HEC token"""
    try:
        event = request.get_json()
        result = splunk_manager.send_event(event)
        status_code = 200 if result.get("success") else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Error sending event to Splunk"
        }), 500

# ============== SURICATA ENDPOINTS ==============
@app.route('/api/suricata/status', methods=['GET'])
def suricata_status():
    """Gets the current status of Suricata"""
    try:
        status = suricata_manager.get_status()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Error getting Suricata status"
        }), 500

@app.route('/api/suricata/set-path', methods=['POST']) # Binary path
def suricata_set_path():
    """Manually sets Suricata binary path"""
    try:
        data = request.get_json()
        
        if not data or 'path' not in data:
            return jsonify({
                "success": False,
                "message": "'path' field is required in JSON"
            }), 400
        
        result = suricata_manager.set_suricata_bin_path(data['path'])
        status_code = 200 if result["success"] else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error setting Suricata path"
        }), 500
    
@app.route('/api/suricata/set-log-path', methods=['POST']) # Log path
def suricata_set_log_path():
    """Manually sets Suricata logs path"""
    try:
        data = request.get_json()
        
        if not data or 'path' not in data:
            return jsonify({
                "success": False,
                "message": "'path' field is required in JSON"
            }), 400
        
        result = suricata_manager.set_suricata_log_path(data['path'])
        status_code = 200 if result["success"] else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error setting Suricata log path"
        }), 500

@app.route('/api/suricata/start', methods=['POST'])
def suricata_start():
    """Starts Suricata"""
    try:
        result = suricata_manager.start()
        status_code = 200 if result["success"] else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Error starting Suricata"
        }), 500

@app.route('/api/suricata/stop', methods=['POST'])
def suricata_stop():
    """Stops Suricata"""
    try:
        result = suricata_manager.stop()
        status_code = 200 if result["success"] else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Error stopping Suricata"
        }), 500


@app.route('/api/suricata/alerts', methods=['GET'])
def suricata_alerts():
    """Retrieves alerts from Suricata"""
    try:
        severity = request.args.get('severity', default="Any", type=str)
        protocol = request.args.get('protocol', default="Any", type=str)
        timestamp_from = request.args.get('timestamp_from', default=None, type=str)
        timestamp_to = request.args.get('timestamp_to', default=None, type=str)
        cursor_next = request.args.get('cursor_next', default=None, type=int)
        cursor_prev = request.args.get('cursor_prev', default=None, type=int)
        result = suricata_manager.get_alerts(severity=severity, protocol=protocol, timestamp_from=timestamp_from, timestamp_to=timestamp_to, cursor_next=cursor_next, cursor_prev=cursor_prev)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error retrieving Suricata alerts"
        }), 500

@app.route('/api/suricata/cve-details')
def suricata_cve_details():
    """Fetches CVE details from NVD API"""
    try:
        cve_id = request.args.get('cveId', default=None, type=str)
        if not cve_id:
            return jsonify({
                "success": False,
                "message": "'cveId' query parameter is required"
            }), 400
        
        result = suricata_manager.get_cve_details(cve_id)
        status_code = 200 if result.get("success") else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error fetching CVE details"
        }), 500

@app.route('/api/suricata/every_alert')
def suricata_every_alert():
    """Retrieves every alert from Suricata"""
    try:
        result = suricata_manager.get_every_alert()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error retrieving every Suricata alert"
        })

# ============== ERROR HANDLING ==============
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "message": "The requested route does not exist in the API"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "message": str(error)
    }), 500

def signal_handler(signal, frame):
    print("\n\n[!] Shutting down HoneyDash...")
    print("[!] Restoring any modified configurations...\n")
    cowrie_manager.cleanup()
    sys.exit(0)


if __name__ == '__main__':
    # Check if running as root
    if os.geteuid() != 0:
        print("[!] WARNING: HoneyDash is not running as root!")
        print("[!] Some functionalities (installation, iptables configuration) will not be available.")
        print("[!] For full functionality, run with: sudo python3 app.py")
        sys.exit(1)
    if os.readlink(f"/proc/{os.getppid()}/exe") != '/usr/bin/sudo':
        print("[!] WARNING: HoneyDash is running with real UID 0 (root). This is not recommended for security reasons.")
        print("[!] Run HoneyDash under a non-root user with sudo privileges instead.")
        sys.exit(1)
    
    print("\n[+] Starting HoneyDash...")
    print("[+] API available at: http://localhost:5000")
    print("[+] Documentation: http://localhost:5000/\n")
    
    signal(SIGINT, signal_handler)

    # Start Cowrie manager
    cowrie_manager = CowrieManager()
    # Start Dionaea manager
    dionaea_manager = DionaeaManager()
    # Start DDoSPot manager
    ddospot_manager = DDoSPotManager()
    # Start Splunk manager
    splunk_manager = SplunkManager()
    # Start Suricata manager
    suricata_manager = SuricataManager()

    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False) # Set to False to avoid running the initialization twice