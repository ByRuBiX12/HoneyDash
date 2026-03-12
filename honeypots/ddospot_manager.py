import os
import subprocess
import random
import re
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import ipaddress

class DDoSPotManager:
    """DDoSPot Honeypot Manager"""

    def __init__(self):
        self.container_name = "honeydash-ddospot"
        self.data_dir = Path("/opt/honeydash/ddospot-data")
        self.logs_dir = Path("/opt/honeydash/ddospot-data/logs")
        self.db_dir = Path("/opt/honeydash/ddospot-data/db")
        self.install_path = Path("/opt/ddospot") # Installation path for DDoSPot
        docker_installed = self._detect_docker_installation()
        ddospot_container = self._detect_container()
        if not docker_installed:
            print("[-] Docker is not installed. Please install Docker to use DDoSPot honeypot.")
        if not ddospot_container:
            print(f"[-] DDoSPot container '{self.container_name}' not found")
        else:
            print(f"[+] DDoSPot container '{self.container_name}' found")

    def _detect_docker_installation(self):
        """Looks for Docker"""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
        
    def _detect_container(self):
        """Looks for DDoSPot container"""
        try:
            result = subprocess.run(
                ["docker", "ps", "-a", "--filter", f"name={self.container_name}"],
                capture_output=True,
                text=True
            )
            return self.container_name in result.stdout
        except Exception:
            return False
        
    def is_installed(self):
        """Checks if DDoSPot Docker container is installed"""
        if not self._detect_docker_installation():
            return False
        return self._detect_container()
    
    def get_status(self):
        """Get the current status of DDoSPot"""
        if not self._detect_docker_installation():
            return {
                "installed": False,
                "running": False,
                "message": "Docker is not installed"
            }
        
        if not self.is_installed():
            return {
                "installed": False,
                "running": False,
                "message": "DDoSPot container is not installed"
            }
      
        return {
            "installed": True,
            "running": self._is_running(),
            "container_name": self.container_name,
            "data_dir": str(self.data_dir),
            "message": "DDoSPot is running" if self._is_running() else "DDoSPot is stopped"
        }
    
    def _is_running(self):
        """Checks if DDoSPot Docker container is running"""
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={self.container_name}", "--filter", "status=running"],
                capture_output=True,
                text=True
            )
            return self.container_name in result.stdout
        except Exception as e:
            print(f"[-] Error checking DDoSPot status: {e}")
            return False
        
    def install(self):
        """Installs DDoSPot using Docker"""
        try:
            if not self._detect_docker_installation():
                return {
                    "success": False,
                    "message": "Docker is not installed. Please install Docker first."
                }
            
            if self.is_installed():
                return {
                    "success": False,
                    "message": f"DDoSPot container already exists: {self.container_name}"
                }
            
            print("[!] Cloning DDoSPot repository...")
            clone_result = subprocess.run([
                "git", "clone", "https://github.com/aelth/ddospot",
                str(self.install_path)
            ], capture_output=True, text=True)
            
            if clone_result.returncode != 0:
                return {
                    "success": False,
                    "message": "Error cloning DDoSPot repository",
                    "error": clone_result.stderr
                }
            
            print("[!] Setting up virtual environment in Dockerfile...")
            dockerfile_path = self.install_path / "ddospot" / "Dockerfile"
            try:
                with open(dockerfile_path, 'r') as f:
                    content = f.read()
                
                # Use Alpine 3.18 instead of edge (has Python 3.11, which includes 'imp' module)
                content = content.replace(
                    'FROM alpine:edge',
                    'FROM alpine:3.18'
                )
                
                content = content.replace(
                    'RUN pip3 install --upgrade pip\nRUN pip3 install -r /ddospot/requirements.txt',
                    'RUN python3 -m venv /ddospot/venv\n'
                    'RUN /ddospot/venv/bin/pip install --upgrade pip\n'
                    'RUN /ddospot/venv/bin/pip install -r /ddospot/requirements.txt'
                )
                
                content = content.replace(
                    'RUN chown ddospot.ddospot -R /ddospot/*',
                    'RUN chown ddospot:ddospot -R /ddospot/*'
                )

                content = content.replace(
                    'CMD ["python3", "ddospot.py", "-n"]',
                    'CMD ["/ddospot/venv/bin/python3", "ddospot.py", "-n"]'
                )
                
                with open(dockerfile_path, 'w') as f:
                    f.write(content)
                    
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Error patching Dockerfile: {str(e)}"
                }
            
            os.makedirs(self.data_dir, exist_ok=True)
            os.makedirs(self.logs_dir, exist_ok=True)
            os.makedirs(self.db_dir, exist_ok=True)
            
            # Allow container writes
            subprocess.run(["chmod", "-R", "777", str(self.data_dir)], check=False)
            
            print("[!] Building DDoSPot Docker image...")
            build_result = subprocess.run(
                ["docker", "compose", "build"],
                cwd=str(self.install_path),
                capture_output=True,
                text=True
            )
            if build_result.returncode != 0:
                return {
                    "success": False,
                    "message": "Error building DDoSPot Docker image",
                    "error": build_result.stderr
                }
            
            images = subprocess.run(
                ["docker", "images", "--format", "{{.Repository}}"],
                capture_output=True,
                text=True
            )
            image_name = None
            for line in images.stdout.strip().split('\n'):
                if 'ddospot' in line or 'simpledns' in line:
                    image_name = line
                    break
            if not image_name:
                return {
                    "success": False,
                    "message": "DDoSPot image was not built successfully",
                    "error": f"Available images: {images.stdout}"
                }
            
            print(f"[!] Creating container with image: {image_name}")
            create_result = subprocess.run(
                f"docker create --name {self.container_name} --restart unless-stopped --network host" 
                f" -v {self.logs_dir}:/ddospot/logs"
                f" -v {self.db_dir}:/ddospot/db"
                f" {image_name}",
                shell=True,
                capture_output=True,
                text=True
            ) 
            if create_result.returncode != 0:
                return {
                    "success": False,
                    "message": "Error creating DDoSPot container",
                    "error": create_result.stderr
                }
            
            print("[+] DDoSPot installed successfully!")
            print(f"[+] Container Name: {self.container_name}")
            print(f"[+] Data Directory: {self.data_dir}")
            print("[+] Exposed Ports: 19/udp, 53/tcp/udp, 123/udp, 161/udp, 1900/udp")

            return {
                "success": True,
                "message": "DDoSPot Docker container installed successfully",
                "container_name": self.container_name,
                "data_dir": str(self.data_dir)
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Error during installation: {str(e)}"
            }
        
    def start(self):
        """Start DDoSPot container"""
        try:
            if not self.is_installed():
                return {
                    "success": False,
                    "message": "DDoSPot is not installed"
                }
            
            if self._is_running():
                return {
                    "success": False,
                    "message": "DDoSPot is already running"
                }
            
            result = subprocess.run(
                ["docker", "start", self.container_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "message": "Error starting DDoSPot",
                    "error": result.stderr
                }
            
            return {
                "success": True,
                "message": "DDoSPot started successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error starting DDoSPot: {str(e)}"
            }
    
    def stop(self):
        """Stop DDoSPot container"""
        try:
            if not self._is_running():
                return {
                    "success": False,
                    "message": "DDoSPot is not running"
                }
            
            result = subprocess.run(
                ["docker", "stop", self.container_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "message": "Error stopping DDoSPot",
                    "error": result.stderr
                }
            
            return {
                "success": True,
                "message": "DDoSPot stopped successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error stopping DDoSPot: {str(e)}"
            }
    
    def _ip_int_to_str(self, ip_int):
        """Convert IP from int32 to string"""
        return str(ipaddress.IPv4Address(ip_int))
    
    def get_logs(self, limit, protocol, timestamp):
        """Get DDoSPot attack logs from SQLite database"""
        try:
            if not self.is_installed():
                return {
                    "success": False,
                    "message": "DDoSPot is not installed",
                    "logs": []
                }
            
            db_path = self.db_dir / f"{protocol}.sqlite3"
            
            if not db_path.exists():
                return {
                    "success": False,
                    "message": f"Database not found: {db_path}",
                    "logs": []
                }
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            if protocol == 'dnspot':
                query = """
                SELECT s.src_ip, s.src_port, d.domain_name, d.dns_type, a.start, a.latest, a.count, a.amplification
                FROM dnspot_attack a
                JOIN dnspot_sources s ON a.src_id = s.src_ip
                JOIN dnspot_domains d ON a.domain_id = d.id
                """
                if timestamp:
                    query += f" WHERE a.start >= '{timestamp}'"
                query += " ORDER BY a.start DESC LIMIT ?"
                
                cursor.execute(query, (limit,))
                rows = cursor.fetchall()
                
                logs = []
                for row in rows:
                    # Severity field heuristic
                    if row[7] >= 10:
                        severity = "high"
                    elif row[7] >= 5:
                        severity = "medium"
                    else:
                        severity = "low"

                    # Number of packets = scan or attack (10 max due to default DDoSPot blacklist)
                    if row[6] >= 8:
                        if severity == "low":
                            severity = "medium"
                        elif severity == "medium":
                            severity = "high"
                    elif row[6] >= 5:
                        if severity == "low":
                            severity = "medium"

                    logs.append({
                        "honeypot": "ddospot",
                        "protocol": "dns",
                        "src_ip": self._ip_int_to_str(row[0]),
                        "src_port": row[1],
                        "domain_name": row[2],
                        "dns_type": row[3],
                        "attack_start": row[4],
                        "attack_end": row[5],
                        "packet_count": row[6],
                        "amplification_factor": row[7],
                        "severity": severity
                    })
            
            elif protocol == 'ntpot':
                query = """
                SELECT s.src_ip, s.src_port, a.mode, a.start, a.latest, a.count, a.request_size, a.response_size
                FROM ntpot_attack a
                JOIN ntpot_sources s ON a.src_id = s.src_ip
                """
                if timestamp:
                    query += f" WHERE a.start >= '{timestamp}'"
                query += " ORDER BY a.start DESC LIMIT ?"

                cursor.execute(query, (limit,))
                rows = cursor.fetchall()
    
                logs = []
                for row in rows:
                    # Amplification factor calculation
                    if row[6] != 0:
                        amplification = round(row[7] / row[6], 2)
                    else:
                        amplification = 0

                    # Severity field heuristic
                    mode = row[2]
                    severity = "unknown"
                    if mode == 7: # monlist (obsolete but highly abused)
                        severity = "high"
                        mode = "7 (monlist)"
                    elif mode == 6: # control message (can be abused for reflection)
                        if amplification >= 10:
                            severity = "high"
                        else:
                            severity = "medium"
                        mode = "6 (control)"
                    elif mode == 3: # client mode (low risk)
                        if amplification > 1:
                            severity = "medium"
                        else:
                            severity = "low"
                        mode = "3 (client)"
                    else:
                        mode = f"{mode} (unknown)"

                    # Number of packets = scan or attack (10 max due to default DDoSPot blacklist)
                    if row[5] >= 8:
                        if severity == "low":
                            severity = "medium"
                        elif severity == "medium":
                            severity = "high"
                    elif row[5] >= 5:
                        if severity == "low":
                            severity = "medium"

                    logs.append({
                        "honeypot": "ddospot",
                        "protocol": "ntp",
                        "src_ip": self._ip_int_to_str(row[0]),
                        "src_port": row[1],
                        "mode": mode,
                        "attack_start": row[3],
                        "attack_end": row[4],
                        "packet_count": row[5],
                        "amplification_factor": amplification,
                        "severity": severity
                    })

            elif protocol == 'genericpot': # SNMP
                query = """
                SELECT s.src_ip, s.src_port, a.dst_port, a.start, a.latest, a.count, a.request_size, a.response_size
                FROM genericpot_attack a
                JOIN genericpot_sources s ON a.src_id = s.src_ip
                """
                if timestamp:
                    query += f" WHERE a.start >= '{timestamp}'"
                query += " ORDER BY a.start DESC LIMIT ?"
                
                cursor.execute(query, (limit,))
                rows = cursor.fetchall()
                
                logs = []
                for row in rows:
                    # Amplification factor calculation
                    if row[6] != 0:
                        amplification = round(row[7] / row[6], 2)
                    else:
                        amplification = 0

                    # Severity field heuristic
                    if amplification >= 10:
                        severity = "high"
                    elif amplification >= 5:
                        severity = "medium"
                    else:
                        severity = "low"

                    # Number of packets = scan or attack (10 max due to default DDoSPot blacklist)
                    if row[5] >= 8:
                        if severity == "low":
                            severity = "medium"
                        elif severity == "medium":
                            severity = "high"
                    elif row[5] >= 5:
                        if severity == "low":
                            severity = "medium"

                    logs.append({
                        "honeypot": "ddospot",
                        "protocol": "snmp",
                        "src_ip": self._ip_int_to_str(row[0]),
                        "src_port": row[1],
                        "dst_port": row[2],
                        "attack_start": row[3],
                        "attack_end": row[4],
                        "packet_count": row[5],
                        "amplification_factor": amplification,
                        "severity": severity
                    })

            elif protocol == 'ssdpot':
                query = """
                SELECT s.src_ip, s.src_port, a.st, a.start, a.latest, a.count, a.request_size, a.response_size, a.mx
                FROM ssdpot_attack a
                JOIN ssdpot_sources s ON a.src_id = s.src_ip
                """
                if timestamp:
                    query += f" WHERE a.start >= '{timestamp}'"
                query += " ORDER BY a.start DESC LIMIT ?"
                
                cursor.execute(query, (limit,))
                rows = cursor.fetchall()

                logs = []
                for row in rows:
                    # Amplification factor calculation
                    if row[6] != 0:
                        amplification = round(row[7] / row[6], 2)
                    else:
                        amplification = 0

                    # Severity field heuristic
                    severity = "low"
                    if row[2] == "ssdp:all" or amplification >= 10: # st = ssdp:all requests for every device
                        severity = "high"
                    elif amplification >= 5:
                        severity = "medium"
                    
                    if row[8] <= 2: # low mx = short response time
                        if severity == "medium":
                            severity = "high"
                        elif severity == "low":
                            severity = "medium"

                    # Number of packets = scan or attack (10 max due to default DDoSPot blacklist)
                    if row[5] >= 8:
                        if severity == "low":
                            severity = "medium"
                        elif severity == "medium":
                            severity = "high"
                    elif row[5] >= 5:
                        if severity == "low":
                            severity = "medium"

                    logs.append({
                        "honeypot": "ddospot",
                        "protocol": "ssdp",
                        "src_ip": self._ip_int_to_str(row[0]),
                        "src_port": row[1],
                        "st": row[2],
                        "mx": row[8],
                        "attack_start": row[3],
                        "attack_end": row[4],
                        "packet_count": row[5],
                        "amplification_factor": amplification,
                        "severity": severity
                    })

            elif protocol == 'chargenpot':
                query = """
                SELECT s.src_ip, s.src_port, a.start, a.latest, a.count, a.request_size, a.response_size
                FROM chargenpot_attack a
                JOIN chargenpot_sources s ON a.src_id = s.src_ip
                """
                if timestamp:
                    query += f" WHERE a.start >= '{timestamp}'"
                query += " ORDER BY a.start DESC LIMIT ?"
                
                cursor.execute(query, (limit,))
                rows = cursor.fetchall()
                
                logs = []
                for row in rows:
                    # Amplification factor calculation
                    if row[5] != 0:
                        amplification = round(row[6] / row[5], 2)
                    else:
                        amplification = 0

                    # Severity field heuristic
                    if amplification >= 5:
                        severity = "high"
                    else:
                        severity = "low"

                    # Number of packets = scan or attack (10 max due to default DDoSPot blacklist)
                    if row[4] >= 8:
                        if severity == "low":
                            severity = "high"
                    elif row[4] >= 3:
                        if severity == "low":
                            severity = "medium"

                    logs.append({
                        "honeypot": "ddospot",
                        "protocol": "chargen",
                        "src_ip": self._ip_int_to_str(row[0]),
                        "src_port": row[1],
                        "attack_start": row[2],
                        "attack_end": row[3],
                        "packet_count": row[4],
                        "amplification_factor": amplification,
                        "severity": severity
                    })
            
            return {
                "success": True,
                "message": f"Found {len(logs)} attack logs",
                "logs": logs
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error reading DDoSPot logs: {str(e)}",
                "logs": []
            }