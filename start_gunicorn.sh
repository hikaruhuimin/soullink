#!/bin/bash
cd ./soullink
pkill -f gunicorn 2>/dev/null
sleep 1
nohup gunicorn -w 2 -b 0.0.0.0:5000 wsgi:flask_app --error-logfile gunicorn-error.log --access-logfile gunicorn-access.log > /dev/null 2>&1 &
sleep 3
ps aux | grep gunicorn | grep -v grep
