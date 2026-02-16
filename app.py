from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import sys
from pathlib import Path
from signal import signal, SIGINT
import pwd

from honeypots.cowrie_manager import CowrieManager
from honeypots.dionaea_manager import DionaeaManager
from siem.splunk_manager import SplunkManager

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
    """Retrieves Cowrie logs with optional filtering""" # El usuario filtrará por límite de logs, tipo de evento y timestamp. Más tarde podrá ocultar campos que no quiera ver <- TODO
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

# TODO: ENDPOINT PARA LOGS

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
        })

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
        })

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
        })
    
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
        })

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
    # Start Splunk manager
    splunk_manager = SplunkManager()

    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False) # Set to False to avoid running the initialization twice