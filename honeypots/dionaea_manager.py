import os
import subprocess
import random
import re
import json
from pathlib import Path
import shutil
import hashlib
import datetime
from itertools import islice


class DionaeaManager:
    """Dionaea honeypot manager using Docker"""

    def __init__(self):
        self.container_name = "honeydash-dionaea"
        self.image_name = "dinotools/dionaea:latest"
        self.data_dir = Path("/opt/honeydash/dionaea-data")
        docker_installed = self._detect_docker_installation()
        dionaea_container = self._detect_container()
        if not docker_installed:
            print("[-] Docker is not installed. Please install Docker to use Dionaea honeypot.")
        if not dionaea_container:
            print(f"[-] Dionaea container '{self.container_name}' not found")
        else:
            print(f"[+] Dionaea container '{self.container_name}' found")
        

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
        """Looks for Dionaea container"""
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
        """Checks if Dionaea Docker container is installed"""
        if not self._detect_docker_installation():
            return False
        return self._detect_container()
    
    def get_status(self):
        """Get the current status of Dionaea"""
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
                "message": "Dionaea container is not installed"
            }
      
        return {
            "installed": True,
            "running": self._is_running(),
            "container_name": self.container_name,
            "data_dir": str(self.data_dir),
            "message": "Dionaea is running" if self._is_running() else "Dionaea is stopped"
        }
    
    def _is_running(self):
        """Checks if Dionaea Docker container is running"""
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={self.container_name}", "--filter", "status=running"],
                capture_output=True,
                text=True
            )
            return self.container_name in result.stdout
        except Exception as e:
            print(f"[-] Error checking Dionaea status: {e}")
            return False
        
    def install(self):
        """Installs Dionaea using Docker"""
        try:
            # Docker is required (the apt way fails due to missing dependencies)
            if not self._detect_docker_installation():
                return {
                    "success": False,
                    "message": "Docker is not installed. Please install Docker first."
                }
            
            if self.is_installed():
                return {
                    "success": False,
                    "message": f"Dionaea container already exists: {self.container_name}"
                }
            
            # Data directory
            os.makedirs(self.data_dir, exist_ok=True)
            os.makedirs(self.data_dir / "logs", exist_ok=True)
            os.makedirs(self.data_dir / "binaries", exist_ok=True)
            os.makedirs(self.data_dir / "bistreams", exist_ok=True)
            os.makedirs(self.data_dir / "http" / "root", exist_ok=True)
            os.makedirs(self.data_dir / "ftp" / "root", exist_ok=True)
            os.makedirs(self.data_dir / "tftp" / "root", exist_ok=True)
            os.makedirs(self.data_dir / "printer" / "root", exist_ok=True)
            os.makedirs(self.data_dir / "sip", exist_ok=True)
            os.makedirs(self.data_dir / "sqlite", exist_ok=True)
            
            # Copy static/conf/root/ to http/root
            static_root = Path("static/confs/root")
            http_root = self.data_dir / "http" /"root"
            try:
                shutil.copytree(static_root, http_root, dirs_exist_ok=True)
            except Exception as e:
                print(f"[-] Error copying static files to http root: {e}")
                return {
                    "success": False,
                    "message": f"Error copying static files to http root: {str(e)}"
                }


            # Allow container writes
            subprocess.run(["chmod", "-R", "777", str(self.data_dir)], check=False)
            
            # Docker image
            pull_res = subprocess.run(
                ["docker", "pull", self.image_name],
                capture_output=True,
                text=True
            )
            
            if pull_res.returncode != 0:
                return {
                    "success": False,
                    "message": "Error pulling Dionaea Docker image",
                    "error": pull_res.stderr
                }
            
            # Create container
            create_result = subprocess.run(
                f"docker create --name {self.container_name} --restart unless-stopped --network host \
                -v {self.data_dir}/logs:/opt/dionaea/var/log/dionaea \
                -v {self.data_dir}/binaries:/opt/dionaea/var/lib/dionaea/binaries \
                -v {self.data_dir}/bistreams:/opt/dionaea/var/lib/dionaea/bistreams \
                -v {self.data_dir}/http:/opt/dionaea/var/lib/dionaea/http \
                -v {self.data_dir}/ftp:/opt/dionaea/var/lib/dionaea/ftp \
                -v {self.data_dir}/tftp:/opt/dionaea/var/lib/dionaea/tftp \
                -v {self.data_dir}/printer:/opt/dionaea/var/lib/dionaea/printer \
                -v {self.data_dir}/sqlite:/opt/dionaea/var/lib/dionaea \
                dinotools/dionaea",
                shell=True,
                capture_output=True,
                text=True
            )
            
            if create_result.returncode != 0:
                return {
                    "success": False,
                    "message": "Error creating Dionaea container",
                    "error": create_result.stderr
                }
            
            print("[+] Dionaea installed successfully!")
            print(f"[+] Container name: {self.container_name}")
            print(f"[+] Data directory: {self.data_dir}")
            print(f"[+] Exposed ports: 21, 23, 42, 80, 135, 443, 445, 1433, 1723, 1883, 1900/udp, 3306, 5060, 5060/udp, 5061, 11211")
            
            return {
                "success": True,
                "message": "Dionaea Docker container installed successfully",
                "container_name": self.container_name,
                "data_dir": str(self.data_dir)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error during installation: {str(e)}"
            }
    
    def start(self):
        """Start Dionaea container"""
        try:
            if not self.is_installed():
                return {
                    "success": False,
                    "message": "Dionaea is not installed"
                }
            
            if self._is_running():
                return {
                    "success": False,
                    "message": "Dionaea is already running"
                }
            
            result = subprocess.run(
                ["docker", "start", self.container_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "message": "Error starting Dionaea",
                    "error": result.stderr
                }
            
            return {
                "success": True,
                "message": "Dionaea started successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error starting Dionaea: {str(e)}"
            }
    
    def stop(self):
        """Stop Dionaea container"""
        try:
            if not self._is_running():
                return {
                    "success": False,
                    "message": "Dionaea is not running"
                }
            
            result = subprocess.run(
                ["docker", "stop", self.container_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "message": "Error stopping Dionaea",
                    "error": result.stderr
                }
            
            return {
                "success": True,
                "message": "Dionaea stopped successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error stopping Dionaea: {str(e)}"
            }
    
    def get_logs(self, limit, itype, timestamp):
        """Get Dionaea logs"""
        try:
            if not self._detect_docker_installation():
                return {
                    "success": False,
                    "message": "Docker is not installed"
                }
            if not self._detect_container():
                return {
                    "success": False,
                    "message": "Dionaea is not installed"
                }
            
            log_dir = self.data_dir / "bistreams"
            if not log_dir.exists():
                return {
                    "success": False,
                    "message": "Log directory not found"
                }
            
            logs = []
            counter = 0
            if not timestamp:
                for dir in log_dir.iterdir():
                    if dir.is_dir():
                        for log_file in dir.iterdir():
                            log_type = log_file.name.split("-")[0]
                            if log_type == itype:
                                log_entry = self._to_json(log_file, log_type)
                                if log_entry:
                                    logs.append(log_entry)
                                    counter += 1
                                    if counter >= limit:
                                        break
                        if counter >= limit:
                            break
            else:
                for dir in log_dir.iterdir():
                    if dir.is_dir():
                        for log_file in dir.iterdir():
                            log_type = log_file.name.split("-")[0]
                            log_timestamp = log_file.name.split("-")[5] + "-" + log_file.name.split("-")[6] + "-" + log_file.name.split("-")[7][:-7]
                            if log_type == itype and log_timestamp >= timestamp:
                                log_entry = self._to_json(log_file, log_type)
                                if log_entry:
                                    logs.append(log_entry)
                                    counter += 1
                                    if counter >= limit:
                                        break
                        if counter >= limit:
                            break
            return {
                "success": True,
                "logs": logs
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Error reading log file: {str(e)}"
            }

    def _to_json(self, log_file, log_type):
        """Converts a Dionaea log file to JSON format"""
        if log_type == "httpd":
            with open(log_file, 'r') as f:
                # fist line = request
                request = f.readline().strip()
                user_agent = re.search(r'User-Agent: ([^\\]+)', request)
                ip = re.search(r'Host: ([^\\]+)', request)
                request_type = re.search(r'(GET|POST|HEAD|PUT|DELETE|OPTIONS|TRACE|CONNECT)\s', request)
                endpoint = re.search(r'(GET|POST|HEAD|PUT|DELETE|OPTIONS|TRACE|CONNECT)\s+(\S+)\s+HTTP', request)
                date = log_file.name.split("-")[5] + "-" + log_file.name.split("-")[6] + "-" + log_file.name.split("-")[7][:-7]
                username = re.search(r'username=([^\&]+)', request)
                password = re.search(r'password=([^\']+)', request)
                filename = re.search(r'filename="([^"]+)"', request)
                
                log_entry = {"timestamp": date}
                
                if ip:
                    log_entry["ip"] = ip.group(1)
                if user_agent:
                    log_entry["user_agent"] = user_agent.group(1)
                if request_type:
                    log_entry["request_type"] = request_type.group(1)
                if endpoint:
                    log_entry["endpoint"] = endpoint.group(2)
                if username:
                    log_entry["username"] = username.group(1)
                if password:
                    log_entry["password"] = password.group(1)
                if filename:
                    log_entry["filename"] = filename.group(1)
                
                return log_entry
        elif log_type == "ftpd":
            with open(log_file, 'r') as f:
                content = f.read()
                
                ip = log_file.name.split("-")[3]
                date = log_file.name.split("-")[5] + "-" + log_file.name.split("-")[6] + "-" + log_file.name.split("-")[7][:-7]
                username = re.search(r'USER ([^\\]+)', content)
                password = re.search(r'PASS ([^\\]+)', content)
                filename = re.search(r'STOR ([^\\]+)', content)
                
                log_entry = {"timestamp": date}
                log_entry["ip"] = ip

                if username:
                    log_entry["username"] = username.group(1)
                if password:
                    log_entry["password"] = password.group(1)
                if filename:
                    log_entry["filename"] = filename.group(1)
                    
                return log_entry
    
        elif log_type == "mysqld":
            with open(log_file, 'r') as f:
                content = f.read()
                ip = log_file.name.split("-")[3]
                date = log_file.name.split("-")[5] + "-" + log_file.name.split("-")[6] + "-" + log_file.name.split("-")[7][:-7]
                username = re.search(r'\\x00\\x00\\x00([a-zA-Z0-9_-]+)\\x00', content)

                log_entry = {"timestamp": date}
                log_entry["ip"] = ip

                if username:
                    username = username.group(1)
                    log_entry["username"] = username

                    line_pattern = rf'\\x00\\x00\\x00{re.escape(username)}\\x00[^\n\r]*?(?=\n|\r|$)'
                    line = re.search(line_pattern, content)
                    if line:
                        line_content = line.group(0)
                        # username\x00\x00') = no password was sent
                        hashed_pattern = rf"{re.escape(username)}\\x00\\x00'\)"
                        if re.search(hashed_pattern, line_content):
                            log_entry["password"] = "Password not sent"
                        else:
                            # username\xXX<password>\x00')
                            hash_marker_pattern = rf"{re.escape(username)}\\x[a-fA-F0-9]{{2}}(.+?)\\x00'\)"
                            hash_match = re.search(hash_marker_pattern, line_content)
                            
                            if hash_match:
                                hash = hash_match.group(1)

                                candidates = re.findall(r'(?:^|[^\\x])([a-zA-Z][a-zA-Z0-9_@!#$%^&*()+\-]{3,})', hash)
                                
                                valid = []
                                for candidate in candidates:
                                    if candidate[0] == 'x' and len(candidate) > 2 and re.match(r'^x[0-9a-fA-F]{2}', candidate):
                                            continue
                                    valid.append(candidate)
                                
                                if valid:
                                    log_entry["password"] = valid[-1] 
                                else:
                                    log_entry["password"] = "Password is hashed"
                            else:
                                log_entry["password"] = "Password is hashed"

                return log_entry
        return None
    
    def get_binaries(self, page):
        """Get binaries captured by Dionaea"""
        try:
            if not self._detect_docker_installation():
                return {
                    "success": False,
                    "message": "Docker is not installed"
                }
            if not self._detect_container():
                return {
                    "success": False,
                    "message": "Dionaea is not installed"
                }
            
            binaries_dir = self.data_dir / "binaries"
            if not binaries_dir.exists():
                return {
                    "success": False,
                    "message": "Binaries directory not found"
                }
            files = []
            for f in binaries_dir.iterdir():
                if f.is_file():
                    files.append(f)
            
            total = len(files)
            
            if total == 0:
                return {
                    "success": False,
                    "message": "No binaries found"
                }

            start_idx = (page - 1) * 9
            end_idx = start_idx + 9
            
            if start_idx >= total:
                return {
                    "success": False,
                    "message": "No more binaries available",
                    "total": total,
                    "page": page
                }

            binaries = []
            for binary in files[start_idx:end_idx]:
                binaries.append({
                    "md5hash": hashlib.md5(open(binary, 'rb').read()).hexdigest(),
                    "size": binary.stat().st_size,
                    "timestamp": datetime.datetime.fromtimestamp(os.path.getctime(binary)).strftime("%Y-%m-%d %H:%M:%S")
                })
            
            return {
                "success": True,
                "binaries": binaries,
                "total": total,
                "page": page,
                "total_pages": (total + 9 - 1) // 9
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }