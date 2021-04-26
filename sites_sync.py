#!/usr/bin/env python3

import requests

import argparse
import sys
import json

import urllib3
urllib3.disable_warnings()

parser = argparse.ArgumentParser(description='rsync ispconfig sites')

parser.add_argument('--src-address', metavar='src_addr', required=True, type=str,
                   help='source ispconfig server IP')
parser.add_argument('--src-port', metavar='src_port', default='8080', type=str,
                   help='source ispconfig server port')

parser.add_argument('--src-username', metavar='src_username', required=True, type=str,
                   help='API username on source ispconfig server')
parser.add_argument('--src-password', metavar='src_password', required=True, type=str,
                   help='API password on source ispconfig server')

parser.add_argument('--dst-address', metavar='dst_addr', required=True, type=str,
                   help='destination ispconfig server IP')
parser.add_argument('--dst-port', metavar='dst_port', default='8080', type=str,
                   help='destination ispconfig server port')

parser.add_argument('--dst-username', metavar='dst_username', required=True, type=str,
                   help='API username on destination ispconfig server')
parser.add_argument('--dst-password', metavar='dst_password', required=True, type=str,
                   help='API password on destination ispconfig server')

args = parser.parse_args()

dst_url = 'https://%s:%s/remote/json.php?' % (args.dst_address, args.dst_port)

src_url = 'https://%s:%s/remote/json.php?' % (args.src_address, args.src_port)

def get_command(command, data):
  ndata = {}
  ndata['session_id'] = session_id
  for k,v in data.items():
    ndata[k] = v
  r = requests.post(url + command, json=ndata, verify=False)
  return r.json()['response']

url = src_url

session_id = requests.post(url + 'login', json={'username' : args.src_username, 'password' : args.src_password}, verify=False).json()['response']

source_data = {}
source_data = get_command('sites_web_domain_get', {'primary_id': {}})

dst_data = {}
  
url = dst_url
session_id = requests.post(url + 'login', json={'username' : args.dst_username, 'password' : args.dst_password}, verify=False).json()['response']

dst_data = get_command('sites_web_domain_get', {'primary_id': {}})

result = {}

for src_site in source_data:
  for dst_site in dst_data:
    if src_site['type'] == 'vhost':
      if src_site['domain'] == dst_site['domain']:
        result[src_site['domain']] = { 'src': src_site['document_root'],
                                       'dst': dst_site['document_root'],
                                       'src_user': src_site['system_user'],
                                       'src_group': src_site['system_group'],
                                       'dst_user': dst_site['system_user'],
                                       'dst_group': dst_site['system_group']}

import json
print(json.dumps(result))
