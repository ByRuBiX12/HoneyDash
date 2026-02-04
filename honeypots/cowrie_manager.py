import os
import subprocess
import random
import re
import json
from pathlib import Path


class CowrieManager:
    """Cowrie honeypot manager"""
    
    def __init__(self, cowrie_path=None):
        self.cowrie_path = None # None because it may be auto-detected
        self.config_file = None # None because it may be auto-detected
        self.ssh_config_file = Path("/etc/ssh/sshd_config")
        self.original_ssh_port = 22 # Default SSH port
        self.cowrie_port = 2222 # Cowrie needs to listen on port 2222
        self.state_file = Path("/var/lib/honeydash/cowrie_state.json") # State file to store original config
        self.default_install_path = Path("/opt/cowrie") # Default installation path for Cowrie
        
        # If a path is provided, use it
        if cowrie_path:
            self.cowrie_path = Path(cowrie_path)
            self.config_file = self.cowrie_path / "etc" / "cowrie.cfg"
        else:
            # Try to detect Cowrie automatically
            detected_path = self._detect_cowrie_installation()
            if detected_path:
                self.cowrie_path = detected_path
                self.config_file = self.cowrie_path / "etc" / "cowrie.cfg"
        
    def _detect_cowrie_installation(self):
        """
        Looks for "honeyfs" directory, unique in Cowrie.
        """
        try:
            opt_res = subprocess.run(
                ["find", "/opt", "-name", "honeyfs", "-type", "d", "-path", "*/cowrie/*"],
                capture_output=True,
                text=True,
                timeout=7
            )
            glob_res = subprocess.run(
                ["find", "/", "-name", "honeyfs", "-type", "d", "-path", "*/cowrie/*"],
                capture_output=True,
                text=True,
                timeout=30
            )

            result = opt_res if opt_res.stdout != "" else glob_res

            if result.stdout.strip():
                honeyfs_paths = result.stdout.strip().split('\n')
                for honeyfs_path in honeyfs_paths:
                    # Verify wether the parent directory is a valid Cowrie installation
                    potential_cowrie_path = Path(honeyfs_path).parent
                    if self._is_valid_cowrie_dir(potential_cowrie_path):
                        print(f"[+] Cowrie detected at: {potential_cowrie_path}")
                        return potential_cowrie_path
            
            return None
            
        except subprocess.TimeoutExpired:
            print("[!] Timeout expired")
            return None
        except Exception as e:
            print(f"[!] Error detecting Cowrie installation: {e}")
            return None
    
    def _is_valid_cowrie_dir(self, path):
        """
        Verifies wether a directory is a valid Cowrie installation.
        """
        if not path.exists():
            return False
        
        # Checks for the presence of characteristic directories of Cowrie.
        required_items = [
            path / "bin",
            path / "honeyfs",
            path / "etc"
        ]
        
        return all(item.exists() for item in required_items)
    
    def set_cowrie_path(self, custom_path):
        """
        Manually sets the Cowrie installation path. Useful when automatic detection fails.
        
        Args:
            custom_path: Path to the Cowrie installation directory
            
        Returns:
            dict with success and message
        """
        custom_path = Path(custom_path)
        
        if not self._is_valid_cowrie_dir(custom_path):
            return {
                "success": False,
                "message": f"Path {custom_path} does not seem to be a valid Cowrie installation"
            }
        
        self.cowrie_path = custom_path
        self.config_file = self.cowrie_path / "etc" / "cowrie.cfg"
        
        return {
            "success": True,
            "message": f"Path successfully set to: {custom_path}"
        }
    
    def is_installed(self):
        """Checks if Cowrie is installed"""
        if self.cowrie_path is None:
            detected_path = self._detect_cowrie_installation()
            if detected_path:
                self.cowrie_path = detected_path
                self.config_file = self.cowrie_path / "etc" / "cowrie.cfg"
                return True
            return False
        
        return self._is_valid_cowrie_dir(self.cowrie_path)
    
    def get_status(self):
        """Get the current status of Cowrie"""
        if not self.is_installed():
            return {
                "installed": False,
                "running": False,
                "configured": False,
                "cowrie_path": None,
                "message": "Cowrie is not installed or could not be detected"
            }
        
        is_running = self._is_running()
        is_configured = self._is_properly_configured()
        
        return {
            "installed": True,
            "running": is_running,
            "configured": is_configured,
            "cowrie_path": str(self.cowrie_path),
            "cowrie_port": self.cowrie_port,
            "message": self._get_status_message(is_running, is_configured)
        }
    
    def _is_running(self):
        """Checks if Cowrie process is running"""
        try:
            result = subprocess.run(
                ["pgrep", "-f", "cowrie"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            print(f"[-] Error checking Cowrie status: {e}")
            return False
    
    def _is_properly_configured(self):
        """Checks if Cowrie is configured to listen on port 2222"""
        if not self.config_file.exists():
            return False
        
        try:
            with open(self.config_file, 'r') as f:
                content = f.read()
            
            # [ssh] section
            sections = re.split(r'(\[.*?\])', content)
            
            for i in range(len(sections)):
                if sections[i].strip() == '[ssh]':
                    if i + 1 < len(sections):
                        ssh_content = sections[i + 1]
                        match = re.search(
                            r'^listen_endpoints\s*=\s*tcp:2222:interface=0\.0\.0\.0',
                            ssh_content,
                            flags=re.MULTILINE
                        )
                        return match is not None
            
            return False
            
        except Exception as e:
            print(f"[-] Error checking Cowrie configuration: {e}")
            return False
    
    def _get_status_message(self, running, configured):
        """Generates a human-readable status message"""
        if not configured:
            return "Cowrie installed but not properly configured"
        if running:
            return "Cowrie running properly"
        return "Cowrie configured but stopped"
    
    def install(self):
        """Installs Cowrie"""
        try:
            if self.is_installed():
                return {
                    "success": False, 
                    "message": f"Cowrie is already installed at: {self.cowrie_path}"
                }
            
            # Use default path for installation
            install_path = self.default_install_path
            
            # Create parent directory if it doesn't exist
            os.makedirs(install_path.parent, exist_ok=True)
            
            # Install necessary dependencies
            print("[!] Installing system dependencies...")
            deps_result = subprocess.run(
                "apt-get update && apt-get install -y git python3 python3-venv python3-pip libssl-dev libffi-dev build-essential python3-virtualenv",
                shell=True,
                capture_output=True, 
                text=True
            )
            
            if deps_result.returncode != 0:
                return {
                    "success": False,
                    "message": "Error installing system dependencies",
                    "error": deps_result.stderr,
                    "error_message": deps_result.stdout,
                    "error_code": deps_result.returncode
                }
            
            # Cloning Cowrie repository
            print("[!] Cloning Cowrie repository...")
            clone_result = subprocess.run([
                "git", "clone", "https://github.com/cowrie/cowrie.git",
                str(install_path)
            ], capture_output=True, text=True)
            
            if clone_result.returncode != 0:
                return {
                    "success": False,
                    "message": "Error clonando repositorio de Cowrie",
                    "error": clone_result.stderr
                }
            
            # python3 -m venv cowrie-env
            print("[!] Setting up virtual environment...")
            venv_result = subprocess.run([
                "python3", "-m", "venv", "cowrie-env"
            ], cwd=str(install_path), capture_output=True, text=True) # cwd to indicate where to create the venv
            
            if venv_result.returncode != 0:
                return {
                    "success": False,
                    "message": "Error setting up virtual environment",
                    "error": venv_result.stderr
                }
            
            # Install requirements
            print("[!] Installing Python dependencies...")
            pip_result = subprocess.run([
                f"{install_path}/cowrie-env/bin/pip", "install", "-r",
                f"{install_path}/requirements.txt"
            ], capture_output=True, text=True)
            
            if pip_result.returncode != 0:
                return {
                    "success": False,
                    "message": "Error installing Python dependencies",
                    "error": pip_result.stderr
                }
            
            # Copy default configuration file
            config_dist = install_path / "etc" / "cowrie.cfg.dist"
            config_file = install_path / "etc" / "cowrie.cfg"
            if config_dist.exists():
                subprocess.run(["cp", str(config_dist), str(config_file)])
            
            # Change ownership to the user who will run Cowrie
            sudo_user = os.environ.get("SUDO_USER", "root")
            if sudo_user != "root":
                print(f"[!] Changing ownership to {sudo_user}...")
                chown_result = subprocess.run([
                    "chown", "-R", f"{sudo_user}:{sudo_user}", str(install_path)
                ], capture_output=True, text=True)
                
                if chown_result.returncode != 0:
                    print(f"[!] Warning: Could not change ownership: {chown_result.stderr}")
            
            # Update manager paths
            self.cowrie_path = install_path
            self.config_file = config_file
            
            return {
                "success": True,
                "message": "Cowrie installed successfully",
                "path": str(install_path)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error during installation: {str(e)}"
            }
    
    def configure(self):
        """Configures Cowrie to listen on port 2222"""
        try:
            if not self.is_installed():
                return {"success": False, "message": "Cowrie is not installed or could not be detected"}
            
            # Config file exists?
            if not self.config_file.exists():
                config_dist = self.cowrie_path / "etc" / "cowrie.cfg.dist"
                if config_dist.exists():
                    subprocess.run(["cp", str(config_dist), str(self.config_file)])
                else:
                    return {"success": False, "message": "Configuration file not found"}
            
            # Read configuration
            with open(self.config_file, 'r') as f:
                content = f.read()
            
            # Look for [ssh] section
            sections = re.split(r'(\[.*?\])', content)
            ssh_section_found = False      

            for i in range(len(sections)):
                # [ssh]?
                if sections[i].strip() == '[ssh]':
                    ssh_section_found = True        
                    if i + 1 < len(sections):
                        ssh_content = sections[i + 1]
                        if 'listen_endpoints' in ssh_content:
                            # Modify
                            sections[i + 1] = re.sub(
                                r'^listen_endpoints\s*=.*$',
                                'listen_endpoints = tcp:2222:interface=0.0.0.0',
                                ssh_content,
                                flags=re.MULTILINE
                            )
                        else:
                            # Add
                            sections[i + 1] = '\nlisten_endpoints = tcp:2222:interface=0.0.0.0\n' + ssh_content
                    break
            
            # Add [ssh] if not exists
            if not ssh_section_found:
                sections.insert(0, '[ssh]\nlisten_endpoints = tcp:2222:interface=0.0.0.0\n\n')
            
            # Rejoin all sections
            content = ''.join(sections)
            
            # Save configuration
            with open(self.config_file, 'w') as f:
                f.write(content)
            
            return {
                "success": True,
                "message": "Cowrie successfully configured to listen on port 2222",
                "config_file": str(self.config_file)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error configuring Cowrie: {str(e)}"
            }
    
    def setup_ssh_redirect(self):
        """Configures SSH redirection and iptables rules"""
        try:
            # Check for root privileges
            if os.geteuid() != 0: 
                return {"success": False, "message": "Root privileges are required"}
            
            # Find an available random port
            new_ssh_port = self._find_available_port()
            
            # Save current state
            self._save_state(new_ssh_port)
            
            # Modify SSH configuration
            ssh_result = self._move_ssh_to_port(new_ssh_port)
            if not ssh_result["success"]:
                return ssh_result
            
            # Restart SSH service
            restart_result = subprocess.run(
                ["systemctl", "restart", "sshd"],
                stderr=subprocess.DEVNULL
            )
            restart2_result = subprocess.run(
                ["systemctl", "restart", "ssh"],
                stderr=subprocess.DEVNULL
            )

            # Check if both failed (at least one should succeed)
            if restart_result.returncode != 0 and restart2_result.returncode != 0:
                return {
                    "success": False,
                    "message": "Error restarting SSH service (tried both sshd and ssh)"
                }
            
            # Add iptables rule
            iptables_result = subprocess.run([
                "iptables", "-t", "nat", "-A", "PREROUTING",
                "-p", "tcp", "--dport", "22",
                "-j", "REDIRECT", "--to-port", "2222"
            ], capture_output=True, text=True)
            
            if iptables_result.returncode != 0:
                # Revert changes
                self._restore_ssh_config()
                return {
                    "success": False,
                    "message": "Error configuring iptables rule",
                    "error": iptables_result.stderr
                }
            
            return {
                "success": True,
                "message": f"Redirect configured successfully. Real SSH on port {new_ssh_port}",
                "ssh_port": new_ssh_port,
                "cowrie_port": self.cowrie_port
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error configuring redirect: {str(e)}"
            }
    
    def _find_available_port(self):
        """Finds an available random port between 1024 and 65535"""
        while True:
            port = random.randint(1024, 65535)
            # Check if the port is in use
            result = subprocess.run(
                ["ss", "-tuln"],
                capture_output=True,
                text=True
            )
            if f":{port}" not in result.stdout:
                return port
    
    def _move_ssh_to_port(self, new_port):
        """Moves SSH to a new port in the sshd_config file"""
        try:
            with open(self.ssh_config_file, 'r') as f:
                content = f.read()
            
            # Search and replace the Port line
            pattern = r'^Port\s*\d*'
            new_line = f'Port {new_port}'
            
            if re.search(pattern, content, flags=re.MULTILINE):
                content = re.sub(pattern, new_line, content, flags=re.MULTILINE) # Modify
            else:
                content = f'{new_line}\n' + content # Add
            
            # Save backup
            backup_file = self.ssh_config_file.with_suffix('.bak')
            subprocess.run(["cp", str(self.ssh_config_file), str(backup_file)])
            
            # Save new configuration
            with open(self.ssh_config_file, 'w') as f:
                f.write(content)
            
            return {"success": True, "port": new_port}
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error modifying SSH configuration: {str(e)}"
            }
    
    def _save_state(self, ssh_port):
        """Saves the current state to restore it later"""
        state = {
            "ssh_port": ssh_port,
            "original_ssh_port": self.original_ssh_port,
            "iptables_configured": True
        }
        
        # Create parent directory if it does not exist
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f)
    
    def _restore_ssh_config(self):
        """Restores the original SSH configuration"""
        try:
            backup_file = self.ssh_config_file.with_suffix('.bak')
            if backup_file.exists():
                subprocess.run(["cp", str(backup_file), str(self.ssh_config_file)])
                subprocess.run(["systemctl", "restart", "sshd"], stderr=subprocess.DEVNULL)
                subprocess.run(["systemctl", "restart", "ssh"], stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"Error restoring SSH configuration: {e}")
    
    def start(self):
        """Starts Cowrie"""
        try:
            if not self.is_installed():
                return {"success": False, "message": "Cowrie is not installed"}
            
            if self._is_running():
                return {"success": False, "message": "Cowrie is already running"}
            
            # Start Cowrie
            print("[!] Setting up virtual environment...")
            venv_result = subprocess.run([
                "python3", "-m", "venv", "cowrie-env"
            ], cwd=str(self.cowrie_path), capture_output=True, text=True)
            
            if venv_result.returncode != 0:
                return {
                    "success": False,
                    "message": "Error setting up virtual environment",
                    "error": venv_result.stderr
                }

            # Activating virtual environment
            act_result = subprocess.run([
                f"{self.cowrie_path}/cowrie-env/bin/pip", "install", "-r",
                f"{self.cowrie_path}/requirements.txt"
            ], capture_output=True, text=True)
            if act_result.returncode != 0:
                return {
                    "success": False,
                    "message": "Error installing Python dependencies",
                    "error": act_result.stderr
                }
            act2_result = subprocess.run([
                f"{self.cowrie_path}/cowrie-env/bin/python", "-m", "pip", "install", "-e", f"{self.cowrie_path}"
            ], capture_output=True, text=True)
            if act2_result.returncode != 0:
                return {
                    "success": False,
                    "message": "Error installing Cowrie in editable mode",
                    "error": act2_result.stderr
                }

            # Owner of Cowrie must NOT be root
            sudo_user = os.environ.get("SUDO_USER", "root")
            if sudo_user != "root":
                print(f"[!] Ensuring ownership for {sudo_user}...")
                subprocess.run([
                    "chown", "-R", f"{sudo_user}:{sudo_user}", str(self.cowrie_path)
                ], capture_output=True, text=True)

            # Cowrie MUST NOT be run as root, dropping privileges...
            cowrie_bin = self.cowrie_path / "cowrie-env" / "bin" / "cowrie"
            venv_bin = self.cowrie_path / "cowrie-env" / "bin"
            
            # Build the PATH with virtualenv bin at the front
            new_path = f"{venv_bin}:{os.environ.get('PATH', '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin')}"
            
            result = subprocess.run([
                "sudo", "-u", os.environ["SUDO_USER"],
                "env", f"PATH={new_path}",
                f"VIRTUAL_ENV={self.cowrie_path / 'cowrie-env'}",
                str(cowrie_bin), "start"
            ],
                cwd=str(self.cowrie_path),
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "message": "Error starting Cowrie",
                    "error": result.stderr,
                    "stdout": result.stdout
                }
            
            return {
                "success": True,
                "message": "Cowrie started successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error starting Cowrie: {str(e)}"
            }
    
    def stop(self):
        """Stops the Cowrie honeypot"""
        try:
            if not self.is_installed():
                return {"success": False, "message": "Cowrie is not installed"}
            
            if not self._is_running():
                return {"success": False, "message": "Cowrie is not running"}
            
            # Cowrie MUST NOT be run as root, dropping privileges...
            cowrie_bin = self.cowrie_path / "cowrie-env" / "bin" / "cowrie"
            venv_bin = self.cowrie_path / "cowrie-env" / "bin"
            
            # Build the PATH with virtualenv bin at the front
            new_path = f"{venv_bin}:{os.environ.get('PATH', '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin')}"
            
            # Stop Cowrie
            result = subprocess.run([
                "sudo", "-u", os.environ["SUDO_USER"],
                "env", f"PATH={new_path}",
                f"VIRTUAL_ENV={self.cowrie_path / 'cowrie-env'}",
                str(cowrie_bin), "stop"
            ],
                cwd=str(self.cowrie_path),
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "message": "Error stopping Cowrie",
                    "error": result.stderr
                }
            
            return {
                "success": True,
                "message": "Cowrie stopped successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error stopping Cowrie: {str(e)}"
            }
    
    def cleanup(self):
        """Cleans up the configuration: removes iptables rule and restores SSH to port 22"""
        try:
            if os.geteuid() != 0:
                return {"success": False, "message": "Root privileges are required"}
            
            # Remove iptables rule
            subprocess.run([
                "iptables", "-t", "nat", "-D", "PREROUTING",
                "-p", "tcp", "--dport", "22",
                "-j", "REDIRECT", "--to-port", "2222"
            ], capture_output=True, text=True)
            
            # Restore SSH to port 22
            with open(self.ssh_config_file, 'r') as f:
                content = f.read()
            pattern = r'^Port\s*\d*'
            new_line = 'Port 22'
            content = re.sub(pattern, new_line, content, flags=re.MULTILINE)
            
            with open(self.ssh_config_file, 'w') as f:
                f.write(content)

            subprocess.run(["systemctl", "stop", "sshd"], stderr=subprocess.DEVNULL)
            subprocess.run(["systemctl", "stop", "ssh"], stderr=subprocess.DEVNULL)
            
            # Remove state file
            self.state_file.unlink()
            
            return {
                "success": True,
                "message": "Configuration restored. SSH is back to port 22"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error cleaning up configuration: {str(e)}"
            }
