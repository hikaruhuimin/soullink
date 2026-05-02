#!/usr/bin/env python3
import os
import signal
import subprocess
import time

os.chdir('./soullink')

# Kill existing gunicorn
try:
    os.kill(os.getpgid(os.getppid()), signal.SIGTERM)
except:
    pass

subprocess.run(['pkill', '-f', 'gunicorn'], capture_output=True)
time.sleep(1)

# Start gunicorn
subprocess.Popen([
    'gunicorn', '-w', '2', '-b', '0.0.0.0:5000', 
    'wsgi:flask_app',
    '--error-logfile', 'gunicorn-error.log',
    '--access-logfile', 'gunicorn-access.log'
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

time.sleep(3)
print("Gunicorn started!")
