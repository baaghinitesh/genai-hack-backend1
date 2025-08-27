#!/usr/bin/env python3
"""
Start script for the Manga Mental Wellness Backend.
This script starts the FastAPI server with proper configuration.
"""

import uvicorn
import sys
import os

def main():
    """Start the backend server."""
    print("🚀 Starting Manga Mental Wellness Backend...")
    print("📡 Socket.IO enabled for real-time progress updates")
    print("🎨 Imagen 4.0 for image generation")
    print("🗣️ Chirp 3: HD for speech synthesis")
    print("📊 Streaming panel-by-panel generation")
    print("-" * 50)
    
    try:
        # Ensure service account is available for signed URLs
        sa_env = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        local_sa = os.path.join(os.path.dirname(__file__), "servicekey.json")
        if not sa_env and os.path.isfile(local_sa):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = local_sa
            print(f"🔐 Using service account: {local_sa}")

        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
