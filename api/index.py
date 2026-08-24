import os
import sys

# Ensure server module path is accessible for Python serverless runtime
server_dir = os.path.join(os.path.dirname(__file__), "..", "server")
if server_dir not in sys.path:
    sys.path.insert(0, server_dir)

from main import app
