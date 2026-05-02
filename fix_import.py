import sys
content = open('routes_supplementary.py','r').read()
old = 'from flask import request, jsonify, session, render_template, redirect, url_for'
new = old + '\nfrom flask_login import current_user'
content = content.replace(old, new, 1)
open('routes_supplementary.py','w').write(content)
print('done')
