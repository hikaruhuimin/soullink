#!/usr/bin/env python3
"""WSGI wrapper - import app directly for gunicorn"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

app.wsgi_app = app.wsgi_app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
