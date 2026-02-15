import os
import subprocess
import random
import re
import json
from pathlib import Path


class DionaeaManager:
    """Dionaea honeypot manager"""

    def __init__(self):
        self.dionaea_path = None # None because it may be auto-detected
        # TODO: Tiene que ser configurado? Se necesita archivo de configuración?
        self.default_install_path = Path("/opt/dionaea") # Default installation path for Dionaea

        # Try to detect Dionaea automatically
        detected_path = self._detect_dionaea_installation()
        if detected_path:
            self.dionaea_path = detected_path

    def _detect_dionaea_installation(self):
        """Look for "dionaea.cfg" file inside /etc/dionaea"""
        try:
            # /opt search first
            opt_res = None
            try:
                opt_res = subprocess.run(
                    ["find", "/opt", "-name", "dionaea.cfg", "-path", "*/dionaea/etc/dionaea*", "-print", "-quit"],
                    capture_output=True,
                    text=True,
                    timeout=7
                )
            except subprocess.TimeoutExpired:
                print("[!] Timeout searching in /opt, continuing with global search...")
        
            if opt_res and opt_res.stdout.strip():
                result = opt_res
            else:
                glob_res = subprocess.run(
                    ["find", "/", "-name", "dionaea.cfg", "-path", "*/dionaea/etc/dionaea*", "-print", "-quit"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                result = glob_res
            if result.stdout.strip():
                dionaea_cfg_paths = result.stdout.strip().split('\n')
                for dionaea_cfg_path in dionaea_cfg_paths:
                    # Verify wether the parent directory is a valid Dionaea installation
                    potential_dionaea_path = Path(dionaea_cfg_path).parent.parent.parent
                    if self._is_valid_dionaea_dir(potential_dionaea_path):
                        print(f"[+] Dionaea detected at: {potential_dionaea_path}")
                        return potential_dionaea_path
            
            return None
            
        except subprocess.TimeoutExpired:
            print("[!] Timeout expired")
            return None
        except Exception as e:
            print(f"[!] Error detecting Dionaea installation: {e}")
            return None
        
    def _is_valid_dionaea_dir(self, path):
        """
        Verifies wether a directory is a valid Dionaea installation.
        """
        if not path.exists():
            return False
        
        # Checks for the presence of characteristic directories of Dionaea.
        required_items = [
            path / "bin",
            path / "etc",
            path / "lib"
        ]
        
        for item in required_items:
            if not item.exists():
                return False
        return True
    
    def set_dionaea_path(self, custom_path):
        """
        Manually sets the Dionaea installation path. Useful when automatic detection fails.
        
        Args:
            custom_path: Path to the Dionaea installation directory
            
        Returns:
            dict with success and message
        """
        custom_path = Path(custom_path)
        
        if not self._is_valid_dionaea_dir(custom_path):
            return {
                "success": False,
                "message": f"Path {custom_path} does not seem to be a valid Dionaea installation"
            }
        
        self.dionaea_path = custom_path
        # self.config_file = self.dionaea_path / ???
        
        return {
            "success": True,
            "message": f"Path successfully set to: {custom_path}"
        }
    
    def is_installed(self):
        """Checks if Dionaea is installed"""
        if self.dionaea_path is None:
            detected_path = self._detect_dionaea_installation()
            if detected_path:
                self.dionaea_path = detected_path
                # self.config_file = self.dionaea_path / ???
                return True
            return False
        
        return self._is_valid_dionaea_dir(self.dionaea_path)
    
    def get_status(self):
        """Get the current status of Dionaea"""
        if not self.is_installed():
            return {
                "installed": False,
                "running": False,
                # "configured": False,
                "dionaea_path": None,
                "message": "Dionaea is not installed or could not be detected"
            }
        
        is_running = self._is_running()
        # is_configured = self._is_properly_configured()
        
        return {
            "installed": True,
            "running": is_running,
            # "configured": is_configured,
            "dionaea_path": str(self.dionaea_path),
            # "dionaea_port": self.dionaea_port,
            # "message": self._get_status_message(is_running, is_configured)
        }
    
    def _is_running(self):
        """Checks if Dionaea process is running"""
        try:
            result = subprocess.run(
                ["pgrep", "-f", "dionaea"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            print(f"[-] Error checking Dionaea status: {e}")
            return False
        
    def install(self):
        """Installs Dionaea"""
        try:
            if self.is_installed():
                return {
                    "success": False, 
                    "message": f"Dionaea is already installed at: {self.dionaea_path}"
                }
            
            # Use default path for installation
            install_path = self.default_install_path
            
            # Create parent directory if it doesn't exist
            os.makedirs(install_path.parent, exist_ok=True)
            
            # Install necessary dependencies
            print("[!] Installing system dependencies...")
            deps_install = subprocess.run(
                "apt-get update && apt-get install -y autoconf automake build-essential cmake check git libcurl4-openssl-dev libev-dev libglib2.0-dev libloudmouth1-dev libnetfilter-queue-dev libnl-3-dev libpcap-dev libssl-dev libtool libudns-dev python3 python3-dev python3-bson python3-yaml python3-boto3 fonts-liberation",
                shell=True,
                capture_output=True, 
                text=True
            )
            
            if deps_install.returncode != 0:
                return {
                    "success": False,
                    "message": "Error installing system dependencies",
                    "error": deps_install.stderr
                }
            
            # Cloning Dionaea repository to temporary location
            print("[!] Cloning Dionaea repository...")
            temp_clone_path = Path("/tmp/dionaea-clone")
            
            # Remove if exists
            if temp_clone_path.exists():
                subprocess.run(["rm", "-rf", str(temp_clone_path)], check=True)
            
            clone_result = subprocess.run([
                "git", "clone", "https://github.com/DinoTools/dionaea.git",
                str(temp_clone_path)
            ], capture_output=True, text=True)
            
            if clone_result.returncode != 0:
                return {
                    "success": False,
                    "message": "Error cloning Dionaea repository",
                    "error": clone_result.stderr
                }
            
            # Because of incompatibility errors -> disabling Python and emu modules via CMakeLists.txt
            modules_cmake = temp_clone_path / "modules" / "CMakeLists.txt"
            if modules_cmake.exists():
                with open(modules_cmake, 'r') as f:
                    cmake_content = f.read()
                
                cmake_content = cmake_content.replace(
                    "add_subdirectory(python)",
                    "# add_subdirectory(python) # DISABLED because of HoneyDash compatibility issues"
                )
                cmake_content = cmake_content.replace(
                    "if(WITH_MODULE_EMU)",
                    "if(FALSE) # WITH_MODULE_EMU - DISABLED because of HoneyDash path issues"
                )
                
                with open(modules_cmake, 'w') as f:
                    f.write(cmake_content)
                            
            # Temporary directory
            build_path = temp_clone_path / "build"
            if build_path.exists():
                subprocess.run(["rm", "-rf", str(build_path)], check=True)
            
            os.makedirs(build_path, exist_ok=True)
                       
            cmake_result = subprocess.run([
                "cmake", 
                "-DCMAKE_INSTALL_PREFIX:PATH=/opt/dionaea",
                ".."
            ], cwd=str(build_path), capture_output=True, text=True)
            
            if cmake_result.returncode != 0:
                return {
                    "success": False,
                    "message": "Error configuring Dionaea with cmake",
                    "error": cmake_result.stderr,
                    "cmake_output": cmake_result.stdout
                }
            
            # Build
            print("[!] Building Dionaea (this may take a while)...")
            make_result = subprocess.run([
                "make"
            ], cwd=str(build_path), capture_output=True, text=True)
            
            if make_result.returncode != 0:
                return {
                    "success": False,
                    "message": "Error building Dionaea with make",
                    "error": make_result.stderr
                }
            
            # Install
            print("[!] Installing Dionaea to /opt/dionaea...")
            install_result = subprocess.run([
                "make", "install"
            ], cwd=str(build_path), capture_output=True, text=True)
            
            if install_result.returncode != 0:
                return {
                    "success": False,
                    "message": "Error installing Dionaea",
                    "error": install_result.stderr
                }
            
            # Clean up temporary files
            subprocess.run(["rm", "-rf", str(temp_clone_path)])
                        
            # Change ownership to the user who will run Dionaea
            sudo_user = os.environ.get("SUDO_USER", "root")
            if sudo_user != "root":
                print(f"[!] Changing ownership to {sudo_user}...")
                chown_result = subprocess.run([
                    "chown", "-R", f"{sudo_user}:{sudo_user}", str(install_path)
                ], capture_output=True, text=True)
                
                if chown_result.returncode != 0:
                    print(f"[!] Warning: Could not change ownership: {chown_result.stderr}")
            
            # Update manager paths
            self.dionaea_path = install_path
            
            return {
                "success": True,
                "message": "Dionaea installed successfully",
                "path": str(install_path)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error during installation: {str(e)}"
            }