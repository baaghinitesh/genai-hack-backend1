#!/usr/bin/env python3
"""
Startup script for Manga Mental Wellness Frontend
"""

import subprocess
import sys
import os

def main():
    print("🌸 Starting Manga Mental Wellness Frontend...")
    print("Frontend will be available at: http://localhost:8501")
    
    # Change to the project directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Start Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "frontend/streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🌸 Frontend stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start frontend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
