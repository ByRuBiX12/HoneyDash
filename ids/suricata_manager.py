import os
import subprocess
import random
import re
import json
from pathlib import Path
import requests

class SuricataManager:
    def __init__(self):
        self.bin_path = Path("/usr/bin/suricata")
        self.log_path = Path("/var/log/suricata")

    def _is_installed(self):
        """Checks if Suricata is installed"""
        return self.bin_path.exists() and self.log_path.exists()
    
    def get_status(self):
        """Get the current status of Suricata"""
        if not self._is_installed():
            return {
                "installed": False,
                "running": False
            }
        
        try:
            result = subprocess.run(["pgrep", "-f", self.bin_path], capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "installed": True,
                    "running": True,
                    "suricata_path": str(self.bin_path),
                    "log_path": str(self.log_path)
                }
            else:
                return {
                    "installed": True,
                    "running": False,
                    "suricata_path": str(self.bin_path),
                    "log_path": str(self.log_path)
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Error checking Suricata status"
            }
        
    def start(self):
        """Starts Suricata"""
        if not self._is_installed():
            return {
                "success": False,
                "message": "Suricata is not installed"
            }
        
        try:
            result = subprocess.run([
                "systemctl", "start", "suricata"
            ], capture_output=True, text=True)

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "Suricata started successfully"
                }
            else:
                return {
                    "success": False,
                    "message": result.stderr,
                    "error": "Failed to start Suricata"
                }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
        
    def stop(self):
        """Stops Suricata"""
        if not self._is_installed():
            return {
                "success": False,
                "message": "Suricata is not installed"
            }
        
        try:
            result = subprocess.run([
                "systemctl", "stop", "suricata"
            ], capture_output=True, text=True)

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "Suricata stopped successfully"
                }
            else:
                return {
                    "success": False,
                    "message": result.stderr,
                    "error": "Failed to stop Suricata"
                }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
        
    def set_suricata_bin_path(self, bin_path):
        """Manually sets the Suricata installation path"""
        self.bin_path = Path(bin_path)

        if self._is_installed():
            return {
                "success": True,
                "message": f"Suricata binary path set to {self.bin_path}"
            }
        else:
            return {
                "success": False,
                "message": f"Suricata not found at {self.bin_path}. Please check the path and try again."
            }
        
    def set_suricata_log_path(self, log_path):
        """Manually sets the Suricata log path"""
        self.log_path = Path(log_path)

        if self._is_installed():
            return {
                "success": True,
                "message": f"Suricata log path set to {self.log_path}"
            }
        else:
            return {
                "success": False,
                "message": f"Suricata logs not found at {self.log_path}. Please check the path and try again."
            }

    def get_alerts(self, severity, protocol, timestamp_from, timestamp_to, cursor_next, cursor_prev):
        """Retrieves alerts from Suricata logs within a specified time range"""
        try:
            if not self._is_installed():
                return {
                    "success": False,
                    "message": "Suricata is not installed"
                }

            if not timestamp_from:
                timestamp_from = "0000-01-01T00:00:00"
            if not timestamp_to:
                timestamp_to = "9999-12-31T23:59:59"
            
            skip_count = cursor_prev if cursor_prev is not None else cursor_next
            start_position = skip_count
            
            alerts = []
            page_size = 16
            
            log_to_read = "eve.json*"
            for log in sorted(self.log_path.glob(log_to_read)):
                with open(log, "r") as f:
                    for line in f:
                        alert = json.loads(line)                            
                        if alert.get("event_type") != "alert":
                            continue
                        
                        alert_severity = alert.get("alert", {}).get("severity")
                        alert_protocol = alert.get("proto")
                        if severity != "any" and alert_severity != int(severity):
                            continue
                        if protocol != "any" and alert_protocol != protocol:
                            continue
                        
                        alert_time = alert.get("timestamp")
                        if timestamp_from <= alert_time <= timestamp_to:
                            if skip_count > 0:
                                skip_count -= 1
                                continue

                            alerts.append(alert)
                            if len(alerts) > page_size:
                                break
                
                if len(alerts) > page_size:
                    break

            has_next = len(alerts) > page_size
            alerts = alerts[:page_size]

            if len(alerts) == 0:
                return {
                    "success": False,
                    "message": "No alerts found",
                    "alerts": [],
                    "has_next": False,
                    "cursor_next": start_position,
                    "cursor_prev": None
                }

            alerts_filtered = []
            for a in alerts:
                metadata = a.get("alert", {}).get("metadata") or {}
                alerts_filtered.append({
                    "source": "suricata",
                    "timestamp": a["timestamp"][:-12], # 1 | not showing miliseconds and timezone
                    "src_ip": a["src_ip"], #2
                    "src_port": a["src_port"], #2
                    "dest_ip": a["dest_ip"], #2
                    "dest_port": a["dest_port"], #2
                    "in_iface": a["in_iface"], #1
                    "protocol": a["proto"], #1
                    "app_proto": a["app_proto"] if "app_proto" in a else "N/A", #2
                    "signature": a["alert"]["signature"] if "signature" in a["alert"] else "N/A", #2 y dudosa: mejor poner respuesta de la API NVD?
                    "category": a["alert"]["category"] if "category" in a["alert"] else "N/A", #1
                    "cve": metadata.get("cve", "N/A"), #1
                    "severity": a["alert"]["severity"] if "severity" in a["alert"] else "N/A", #2
                })
            
            next_cursor = start_position + len(alerts)
            prev_cursor = max(0, start_position - page_size)
            
            return {
                "success": True,
                "alerts": alerts_filtered,
                "has_next": has_next,
                "cursor_next": next_cursor if has_next else None,
                "cursor_prev": prev_cursor if start_position > 0 else None
            }
                            
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "alerts": [],
                "has_next": False,
                "cursor_next": None,
                "cursor_prev": None
            }

    def get_cve_details(self, cve_id):
        """Fetches CVE details from NVD API"""
        try:
            api_cve_id = ""
            for char in cve_id:
                if char == "_":
                    api_cve_id += "-"
                else:
                    api_cve_id += char

            url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={api_cve_id}"
            response = requests.get(url)
            data = response.json()

            cvss_metrics = data.get('vulnerabilities', [{}])[0].get('cve', {}).get('metrics', {}).get('cvssMetricV31', [])
            primary_metric = {}
            for m in cvss_metrics:
                if m.get('type') == 'Primary':
                    primary_metric = m
                    break
            if not primary_metric:
                primary_metric = cvss_metrics[0] if cvss_metrics else {}

            weaknesess_metrics = data.get('vulnerabilities', [{}])[0].get('cve', {}).get('weaknesses', [{}])
            weakness_ids = []
            for w in weaknesess_metrics:
                if w.get('type') == 'Primary':
                    for d in w.get('description', []):
                        weakness_ids.append(d.get('value', 'N/A'))
            if not weakness_ids:
                for w in weaknesess_metrics[0].get('description', []):
                    weakness_ids.append(w.get('value', 'N/A'))

            details = {
                "cve_id": api_cve_id,
                "description": data.get("vulnerabilities", [{}])[0].get("cve", {}).get("descriptions", [{}])[0].get("value", "N/A"),
                "published": data.get("vulnerabilities", [{}])[0].get("cve", {}).get("published", "N/A")[:10],
                "vulnStatus": data.get("vulnerabilities", [{}])[0].get("cve", {}).get("vulnStatus", "N/A"),
                "severity": f"{primary_metric.get('cvssData', {}).get('baseSeverity', 'N/A')} ({primary_metric.get('cvssData', {}).get('baseScore', 'N/A')})",
                "attackVector": primary_metric.get('cvssData', {}).get('attackVector', 'N/A'),
                "privilegesRequired": primary_metric.get('cvssData', {}).get('privilegesRequired', 'N/A'),
                "weaknesses": weakness_ids
            }
            
            return {
                "success": True,
                "cve_details": details
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }
        
# TODO: Hacer función get_every_alert() sin paginación para enviar a Splunk