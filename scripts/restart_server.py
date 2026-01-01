#!/usr/bin/env python3
"""
Restart the Flask server to load latest configuration.
"""

import os
import sys
import subprocess
import signal
import time

def find_flask_processes():
    """Find running Flask/Python server processes."""
    try:
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True
        )
        
        processes = []
        for line in result.stdout.split('\n'):
            if any(keyword in line.lower() for keyword in ['flask', 'app/main.py', 'run.py', 'app.py']):
                if 'grep' not in line and 'restart_server' not in line:
                    parts = line.split()
                    if parts:
                        pid = parts[1]
                        processes.append((pid, line))
        
        return processes
    except Exception as e:
        print(f"Error finding processes: {e}")
        return []

def restart_server():
    """Kill existing server and provide instructions to start new one."""
    print("=" * 70)
    print("🔄 Flask Server Restart Helper")
    print("=" * 70)
    print()
    
    processes = find_flask_processes()
    
    if processes:
        print(f"Found {len(processes)} running Flask process(es):")
        for pid, line in processes:
            print(f"  PID {pid}: {line[:80]}...")
        print()
        
        print("To restart the server:")
        print("  1. Stop the current server:")
        for pid, _ in processes:
            print(f"     kill {pid}")
        print()
        print("  2. Start a new server:")
        print("     python3 run.py")
        print("     # OR")
        print("     flask run --host=0.0.0.0 --port=5001")
        print()
    else:
        print("✅ No Flask server processes found running.")
        print()
        print("To start the server:")
        print("  python3 run.py")
        print("  # OR")
        print("  flask run --host=0.0.0.0 --port=5001")
        print()

if __name__ == '__main__':
    restart_server()

