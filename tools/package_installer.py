import subprocess
import sys
import os
import json
import threading

def run(input_text: str) -> str:
    """
    Install packages in the current directory.
    
    Commands:
    - install <package_name> [package2 ...] : Install one or more packages
    - install_requirements : Install from requirements.txt
    - list : List installed packages
    - freeze : Show all installed packages (like pip freeze)
    - uninstall <package_name> : Uninstall a package
    - search <query> : Search for packages
    - show <package_name> : Show package details
    - create_requirements : Create requirements.txt from current environment
    """
    
    parts = input_text.strip().split()
    
    if not parts:
        return """Available commands:
- install <package_name> [package2 ...] : Install packages
- install_requirements : Install from requirements.txt
- list : List installed packages
- freeze : Show pip freeze output
- uninstall <package_name> : Uninstall a package
- search <query> : Search for packages
- show <package_name> : Show package info
- create_requirements : Create requirements.txt"""
    
    command = parts[0].lower()
    
    try:
        if command == "install":
            if len(parts) < 2:
                return "Error: Please specify package name(s) to install"
            
            packages = parts[1:]
            
            # Use Popen for real-time output streaming
            process = subprocess.Popen(
                [sys.executable, "-m", "pip", "install", "-v"] + packages,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            output_lines = []
            print(f"\nInstalling: {', '.join(packages)}...")
            print("-" * 60)
            
            for line in process.stdout:
                line = line.strip()
                if line:
                    print(line)  # Print in real-time
                    output_lines.append(line)
            
            process.wait()
            
            full_output = "\n".join(output_lines)
            
            if process.returncode == 0:
                return f"SUCCESS: Successfully installed: {', '.join(packages)}\n\n{full_output}"
            else:
                return f"FAILED: Installation failed:\n{full_output}"
        
        elif command == "install_requirements":
            req_file = "requirements.txt"
            if not os.path.exists(req_file):
                return f"Error: {req_file} not found in current directory"
            
            # Use Popen for real-time output streaming
            process = subprocess.Popen(
                [sys.executable, "-m", "pip", "install", "-v", "-r", req_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            output_lines = []
            print(f"\nInstalling from {req_file}...")
            print("-" * 60)
            
            for line in process.stdout:
                line = line.strip()
                if line:
                    print(line)  # Print in real-time
                    output_lines.append(line)
            
            process.wait()
            
            full_output = "\n".join(output_lines)
            
            if process.returncode == 0:
                return f"SUCCESS: Successfully installed packages from {req_file}\n\n{full_output}"
            else:
                return f"FAILED: Installation failed:\n{full_output}"
        
        elif command == "list":
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list"],
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.stdout
        
        elif command == "freeze":
            result = subprocess.run(
                [sys.executable, "-m", "pip", "freeze"],
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.stdout
        
        elif command == "uninstall":
            if len(parts) < 2:
                return "Error: Please specify package name to uninstall"
            
            package = parts[1]
            
            # Use Popen for real-time output
            process = subprocess.Popen(
                [sys.executable, "-m", "pip", "uninstall", "-y", "-v", package],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            output_lines = []
            print(f"\nUninstalling: {package}...")
            print("-" * 60)
            
            for line in process.stdout:
                line = line.strip()
                if line:
                    print(line)  # Print in real-time
                    output_lines.append(line)
            
            process.wait()
            
            full_output = "\n".join(output_lines)
            
            if process.returncode == 0:
                return f"SUCCESS: Successfully uninstalled: {package}\n\n{full_output}"
            else:
                return f"FAILED: Uninstallation failed:\n{full_output}"
        
        elif command == "search":
            if len(parts) < 2:
                return "Error: Please specify search query"
            
            query = " ".join(parts[1:])
            return f"Note: 'pip search' has been disabled. Please search on PyPI: https://pypi.org/search/?q={query}"
        
        elif command == "show":
            if len(parts) < 2:
                return "Error: Please specify package name"
            
            package = parts[1]
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Package '{package}' not found"
        
        elif command == "create_requirements":
            result = subprocess.run(
                [sys.executable, "-m", "pip", "freeze"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                with open("requirements.txt", "w") as f:
                    f.write(result.stdout)
                return f"SUCCESS: Created requirements.txt with {len(result.stdout.splitlines())} packages"
            else:
                return "FAILED: Failed to create requirements.txt"
        
        else:
            return f"Unknown command: {command}\n\nUse without arguments to see available commands"
    
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error: {str(e)}"
