#!/usr/bin/env python3
import subprocess
import sys
import os

os.chdir('/app/data/所有对话/主对话/soullink')

# Start gunicorn
proc = subprocess.Popen([
    sys.executable, '-m', 'gunicorn',
    '-w', '2',
    '-b', '0.0.0.0:5000',
    'wsgi:flask_app'
])

print(f"Started gunicorn with PID {proc.pid}")
