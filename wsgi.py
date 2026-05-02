#!/usr/bin/env python3
"""WSGI wrapper - register supplementary routes before starting"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and configure app
from app import app as flask_app
from routes_supplementary import register_supplementary_routes

# Register supplementary routes
register_supplementary_routes(flask_app)

# Export app for gunicorn
app = flask_app

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=5000, debug=True)
