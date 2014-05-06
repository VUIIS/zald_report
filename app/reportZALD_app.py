#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" app.py

Flask application instantiation/routing
"""
__author__ = 'Benjamin Yvernault <benjamin.c.yvernault@vanderbilt.edu>'
__copyright__ = 'Copyright 2013 Vanderbilt University. All Rights Reserved'

from flask import Flask, render_template, Markup,request,Response
from functools import wraps
import ExtractDataRedcap
 
app = Flask(__name__)  

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    import os
    return username == os.environ['ZQA_USER'] and password == os.environ['ZQA_PASS'] #username == request.environ.get('ZQA_USER') and password == request.environ.get('ZQA_PASS')

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})    

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/zaldreport')
@requires_auth
def home():
    reports = []
    try:
        raw=ExtractDataRedcap.get_data()
        htmlLines = ExtractDataRedcap.html_from_dict(raw)
        rep = ('Quality Assurance per Session per Process', Markup(htmlLines))
        reports.append(rep)
    except Exception as e:
        print e
        reports = [('Uh oh', error_message(e))]    
    return render_template('home.html', reports=reports)

def error_message(e):
    unescaped = '<p><strong>ERROR: Something bad happened </strong>{}</p>'.format(e)
    return Markup(unescaped)
 
if __name__ == '__main__':
    app.run(debug=True)