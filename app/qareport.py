#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" app.py

Flask application instantiation/routing
"""
__author__ = 'Benjamin Yvernault <benjamin.c.yvernault@vanderbilt.edu>'
__copyright__ = 'Copyright 2013 Vanderbilt University. All Rights Reserved'

from flask import Flask, render_template, Markup,request,redirect,url_for,session
from forms import SignupForm, SigninForm
import ExtractDataRedcap
import json,os

app = Flask(__name__)
app.config.from_object('config')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('signup.html', form=form)
        else:
            #adding the new project to the list
            info=json.load(open(os.environ['REPORT_CONFIG']))
            info[form.username.data]={'key':form.key.data,'password':form.password.data,'main':form.main.data.strip().replace(' ','_').lower()}
            json.dump(info, open(os.environ['REPORT_CONFIG'],'w'))
            
            session['username'] = form.username.data
            session['password'] = form.password.data
            return redirect(url_for('report',projects=form.username.data))
    elif request.method == 'GET':
        return render_template('signup.html', form=form)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SigninForm()
     
    if request.method == 'POST':
      if form.validate() == False:
        return render_template('signin.html', form=form)
      else:
        session['username'] = form.username.data
        session['password'] = form.password.data
        return redirect(url_for('report',projects=form.username.data))
                   
    elif request.method == 'GET':
      return render_template('signin.html', form=form)
    
@app.route('/signout')
def signout():
    if 'username' in session:
        session.pop('username', None)
    if 'password' in session:
        session.pop('password', None)
    return redirect(url_for('home'))
  
@app.route('/<projects>')    
def report(projects):
    if 'username' not in session:
        return redirect(url_for('signin'))
    
    info=json.load(open(os.environ['REPORT_CONFIG']))
    if session['username'] not in info.keys() or session['password']!=info[session['username']]['password']:
        return redirect(url_for('signin'))
    elif session['username']!=projects:
        return redirect(url_for('error'))
    else:
        reports = []
        try:
            raw=ExtractDataRedcap.get_data(projects)
            htmlLines = ExtractDataRedcap.html_from_dict(raw,projects)
            rep = ('Quality Assurance per Session per Process', Markup(htmlLines))
            reports.append(rep)
        except Exception as e:
            print e
            reports = [('Uh oh', error_message(e))]
        return render_template('report.html',reports=reports)

@app.route('/')   
def home():
    return render_template('home.html')

@app.route('/error')   
def error():
    if 'username' in session:
        session.pop('username', None)
    if 'password' in session:
        session.pop('password', None)
    
    return render_template('error.html')

def error_message(e):
    unescaped = '<p><strong>Something bad happened </strong>{}</p>'.format(e)
    return Markup(unescaped)

if __name__ == '__main__':
    app.run(debug=True)
