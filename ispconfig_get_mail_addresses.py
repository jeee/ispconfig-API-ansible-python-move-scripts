#!/usr/bin/env python3

import requests

import argparse
import sys
import json

import urllib3
urllib3.disable_warnings()

parser = argparse.ArgumentParser(description='rsync ispconfig sites')
parser.add_argument('--ispconfig_config_backup', metavar='ispconfig_config_backup', default='ispconfig_config_backup.json', type=str,   
                    help='filename of file (to) contain the configuration data')
parser.add_argument('--server', metavar='server', default='127.0.0.1', type=str,   
                    help='ip address or servername of the server')
parser.add_argument('--port', metavar='port', default='8080', type=str,   
                    help='port of the server')
parser.add_argument('--username', metavar='username', type=str,   
                    help='username on the server', required=True)
parser.add_argument('--password', metavar='password', type=str,   
                    help='password on the server', required=True)
args = parser.parse_args()


src_url = 'https://%s:%s/remote/json.php?' % (args.server, args.port)


def get_command(command, data):
  ndata = {}
  ndata['session_id'] = session_id
  for k,v in data.items():
    ndata[k] = v
  r = requests.post(url + command, json=ndata, verify=False)
  return r.json()['response']



url = src_url

session_id = requests.post(url + 'login', json={'username' : args.username, 'password' : args.password}, verify=False).json()['response']



email_boxes = get_command('mail_user_get', {'primary_id': {}})

results = []
for email in email_boxes:
    results.append(email['email'])
    
import json
print(json.dumps(results))
