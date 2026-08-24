import os
import sys

# Compute absolute path to server directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "server"))

if SERVER_DIR not in sys.path:
    sys.path.insert(0, SERVER_DIR)

from main import app
