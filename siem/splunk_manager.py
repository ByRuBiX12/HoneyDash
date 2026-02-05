import json
import subprocess
from pathlib import Path
import base64
import requests
from flask import jsonify
import urllib3

# Disable SSL warnings for self-signed certificates in local development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SplunkManager:
    def __init__(self):
        self.splunk_path = Path("/opt/splunk") # Default Splunk path
        self.splunk_user = "admin" # TODO: Ask user for credentials
        self.splunk_password = "admintfg" # TODO: Ask user for credentials
        self.splunk_host = "https://localhost:8089" # Default Splunk host
        self.splunk_hec_url = "http://localhost:8088/services/collector" # Default HEC URL
        self.splunk_hec_token = None # Will be set when created or found
    
    def _is_installed(self):
        """Check if Splunk is installed"""
        return (self.splunk_path / "bin/splunk").exists()
    
    def get_status(self):
        """Get the current status of Splunk"""
        if not self._is_installed():
            return {
                "installed": False,
                "running": False,
                "token": self.splunk_hec_token
                }
        
        try:
            result = subprocess.run([self.splunk_path / "bin/splunk", "status"], 
                                    capture_output=True, text=True)

            if "splunkd is running" in result.stdout:
                self.search_token()
                return {"installed": True, "running": True, "token": self.splunk_hec_token}
            else:
                return {"installed": True, "running": False, "token": self.splunk_hec_token}

        except Exception as e:
            return {"success": False,
                    "error": str(e),
                    "message": "Error checking Splunk status"}
        
    def start(self):
        """Starts Splunk"""
        if not self._is_installed():
            return {
                "success": False,
                "message": "Splunk is not installed"
            }
        
        try:
            result = subprocess.run([self.splunk_path / "bin/splunk", "start", "--accept-license", "--answer-yes"], 
                                    capture_output=True, text=True)

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "Splunk started successfully"
                }
            else:
                return {
                    "success": False,
                    "message": result.stderr,
                    "error": "Failed to start Splunk"
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
        
    def stop(self):
        """Stops Splunk"""
        if not self._is_installed():
            return {
                "success": False,
                "message": "Splunk is not installed"
            }
        
        try:
            result = subprocess.run([self.splunk_path / "bin/splunk", "stop"], 
                                    capture_output=True, text=True)

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "Splunk stopped successfully"
                }
            else:
                return {
                    "success": False,
                    "message": result.stderr,
                    "error": "Failed to stop Splunk"
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }

    
    # Look for HoneyDash token in Splunk's HTTP Event Collector inputs, NOT another token
    def search_token(self):
        if not self._is_installed():
            return {
                "success": False,
                "message": "Splunk is not installed"
            }
        
        # running? not calling get_status() to avoid infinite loop
        try:
            result = subprocess.run([self.splunk_path / "bin/splunk", "status"], 
                                    capture_output=True, text=True, timeout=5)
            if "splunkd is running" not in result.stdout:
                return {
                    "success": False,
                    "message": "Splunk is not running"
                }
        except Exception:
            return {
                "success": False,
                "message": "Error checking Splunk status"
            }

        url = f"{self.splunk_host}/services/data/inputs/http?output_mode=json"

        auth = base64.b64encode(f"{self.splunk_user}:{self.splunk_password}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth}"
        }

        try:
            r = requests.get(url, headers=headers, verify=False)
            response = r.json()

            for t in response.get("entry", []):
                if t.get("name") == "http://honeydash_token":
                    print("[+] HoneyDash token found in Splunk")
                    self.splunk_hec_token = t.get("content", {}).get("token")
                    return {
                        "success": True,
                        "token": t.get("content", {}).get("token"),
                        "message": "HoneyDash token found in Splunk"
                    }
            self.splunk_hec_token = None
            return {
                "success": False,
                "token": None,
                "message": "HoneyDash token not found in Splunk"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Error searching for token"
            }

    def create_token(self):
        search = self.search_token()  # Check if token already exists before creating a new one
        if search.get("success"):
            print("[!] HoneyDash token already exists in Splunk. Not creating a new one.")
            return {
                "success": True,
                "token": search.get("token"),
                "message": "HoneyDash token already exists"
            }

        url = f"{self.splunk_host}/services/data/inputs/http?output_mode=json"

        auth = base64.b64encode(f"{self.splunk_user}:{self.splunk_password}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth}"
        }

        # Minimum required -> token name
        data = {
            "name": "honeydash_token",
        }

        try:
            r = requests.post(url, data=data, headers=headers, verify=False)

            response = r.json()

            token = response.get("entry", [{}])[0].get("content", {}).get("token")
            self.splunk_hec_token = token

            return {
                "message": "Token successfully created",
                "token": token
            }

        except Exception as e:
            return {
                "message": f"Error: {str(e)}",
                "token": None
            }
            
    def send_event(self, event, sourcetype="honeydash", index="main"):
        """Sends events to Splunk
        
        Args:
            event: Dictionary with event data
            sourcetype: Source type for the event (default: "honeydash")
            index: Splunk index where to store the event (default: "main")
        """
        if not self.splunk_hec_token:
            return {
                "success": False,
                "message": "HEC token not found. Please create or find the token first."
            }
        
        headers = {
            "Authorization": f"Splunk {self.splunk_hec_token}",
            "Content-Type": "application/json"
        }

        try:
            logs = event.get("logs", [])
            size = len(logs)
            errors = []
            for e in logs:
                payload = {
                    "event": e,
                    "sourcetype": sourcetype,
                    "index": index
                }
                r = requests.post(self.splunk_hec_url, headers=headers, json=payload, verify=False)
                if r.status_code != 200:
                    size -= 1
                    errors.append({
                        "event": e,
                        "status_code": r.status_code,
                        "response": r.text
                    })
            if size == 0:
                return {
                    "success": False,
                    "message": "Failed to send any events to Splunk"
                }
            return {
                    "success": True,
                    "message": f"{size} events successfully sent to Splunk (index={index}, sourcetype={sourcetype})"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
