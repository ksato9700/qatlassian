import requests
from jira import JIRA
from jira.exceptions import JIRAError

from requests_oauthlib import OAuth1
from oauthlib.oauth1 import SIGNATURE_RSA
from urllib.parse import parse_qsl

def get_request_token(server, consumer_key, key_cert_data, callback_uri):
    oauth = OAuth1(
        consumer_key,
        signature_method=SIGNATURE_RSA,
        rsa_key=key_cert_data,
        callback_uri=callback_uri
    )

    r = requests.post(
        server + '/plugins/servlet/oauth/request-token',
        verify=True,
        auth=oauth)
    req = dict(parse_qsl(r.text))

    request_token = req['oauth_token']
    return (
        request_token,
        req['oauth_token_secret'],
        '{}/plugins/servlet/oauth/authorize?oauth_token={}'.format(
            server, request_token))

def get_access_token(server, consumer_key, key_cert_data, request_token,
                     request_token_secret, oauth_verifier):
    oauth = OAuth1(
        consumer_key,
        signature_method=SIGNATURE_RSA,
        rsa_key=key_cert_data,
        resource_owner_key=request_token,
        resource_owner_secret=request_token_secret,
        verifier=oauth_verifier
    )
    r = requests.post(
        server + '/plugins/servlet/oauth/access-token',
        verify=True, auth=oauth)
    acc = dict(parse_qsl(r.text))
    return (acc['oauth_token'], acc['oauth_token_secret'])

class JIRAClient:
    def __init__(self, server, consumer_key, key_cert_data,
                 access_token, access_token_secret):
        oauth_dict = {
            'access_token': access_token,
            'access_token_secret': access_token_secret,
            'consumer_key': consumer_key,
            'key_cert': key_cert_data,
        }
        self.jira = JIRA(server, oauth=oauth_dict)

    def emailAddress(self):
        return self.jira.myself()['emailAddress']

    def issues(self, pkey):
        try:
            return self.jira.search_issues('project = "{}"'.format(pkey))
        except JIRAError:
            return None
