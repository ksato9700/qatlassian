import os
from flask import Flask, session, redirect, request
from jira_client import JIRAClient, get_request_token, get_access_token

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
app.server = os.environ['JIRA_SERVER_URL']
app.key_cert_data = os.environ['PRIVATE_KEY']
app.consumer_key = os.environ['CONSUMER_KEY']

@app.route('/')
def index():
    if 'access_token' in session:
        jira = JIRAClient(app.server, app.consumer_key, app.key_cert_data,
                          session['access_token'],
                          session['access_token_secret'])
        ret = '<p>{}</p><br>'.format(jira.emailAddress())

        ret += '<table>'
        for pkey in ('PROJ', 'RED', 'BLUE'):
            issues = jira.issues(pkey)
            if not issues:
                continue
            ret += '<tr><td>{}</td></tr>'.format(
                ','.join((i.key for i in issues)))
        ret += '</table>'
        return ret

    else:
        return '''
        <a href='/login'>login</a>
        '''

@app.route('/login')
def login():
    res = get_request_token(app.server, app.consumer_key, app.key_cert_data,
                            'http://localhost:5000/login2')
    session['request_token'], session['request_token_secret'] = res[:2]
    return redirect(res[2])

@app.route('/login2')
def login2():
    acc = get_access_token(app.server, app.consumer_key,
                           app.key_cert_data,
                           session['request_token'],
                           session['request_token_secret'],
                           request.args.get('oauth_verifier'))
    session['access_token'], session['access_token_secret'] = acc
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('access_token', None)
    return redirect('/')
