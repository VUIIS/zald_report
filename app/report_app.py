#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" app.py

Flask application instantiation/routing
"""
__author__ = 'Benjamin Yvernault <benjamin.c.yvernault@vanderbilt.edu>'
__copyright__ = 'Copyright 2013 Vanderbilt University. All Rights Reserved'

from flask import Flask, render_template, Markup,request
import ExtractDataRedcap
 
app = Flask(__name__)  

@app.route('/')
def my_form():
    return render_template("authentification.html")

@app.route('/', methods=['POST'])
def authentification():
    import os
    project = request.form['Project']
    username = request.form['Username']
    password = request.form['Password']
    if username==os.environ[project+'_USER'] and password==os.environ[project+'_PASS']:
        reports = []
        try:
            raw=ExtractDataRedcap.get_data('KEY_'+project)
            htmlLines = ExtractDataRedcap.html_from_dict(raw,project)
            rep = ('Quality Assurance per Session per Process', Markup(htmlLines))
            reports.append(rep)
        except Exception as e:
            print e
            reports = [('Uh oh', error_message(e))]    
        return render_template('home.html', reports=reports)
    else:
        return render_template("error.html")

def error_message(e):
    unescaped = '<p><strong>Something bad happened </strong>{}</p>'.format(e)
    return Markup(unescaped)
 
if __name__ == '__main__':
    app.run(debug=True)