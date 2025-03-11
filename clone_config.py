#!/usr/bin/env python3

import requests

import argparse
import sys
import json

import urllib3
urllib3.disable_warnings()

parser = argparse.ArgumentParser(description='clone ispconfig setup')
parser.add_argument('--ispconfig_config_backup', metavar='ispconfig_config_backup', default='ispconfig_config_backup.json', type=str,   
                    help='filename of file (to) contain the configuration data')
parser.add_argument('--make_backup', metavar='make_backup', default='True', type=str,   
                    help='make backup to file')
parser.add_argument('--restore_backup', metavar='restore_backup', default='True', type=str,   
                    help='restore backup from file')

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


if args.make_backup.lower() in ['1', 'true']:
  url = src_url

  session_id = requests.post(url + 'login', json={'username' : args.src_username, 'password' : args.src_password}, verify=False).json()['response']
  
  backup_data = {}
  
  backup_data['clients'] = get_command('client_get', {'client_id': {}})
  backup_data['domains'] = get_command('mail_domain_get', {'primary_id': {}})
  backup_data['email_mailboxes'] = get_command('mail_user_get', {'primary_id': {}})

  ### Return mail_alias, mail_forward and mail_catchall all return: alias aliasdomain catchall forward 
  #backup_data['mail_alias'] = get_command('mail_alias_get', {'primary_id': {}})
  #backup_data['mail_forward'] = get_command('mail_forward_get', {'primary_id': {}})
  backup_data['mail_types'] = get_command('mail_catchall_get', {'primary_id': {}})
  
  ### sites_web_domain, sites_web_subdomain & sites_web_aliasdomain return same: subdomain vhost alias
  #backup_data['sites_web_domain'] = get_command('sites_web_domain_get', {'primary_id': {}})
  #backup_data['sites_web_subdomain'] = get_command('sites_web_subdomain_get', {'primary_id': {}})
  backup_data['sites_web'] = get_command('sites_web_aliasdomain_get', {'primary_id': {}})

  backup_data['sites_ftp_user'] = get_command('sites_ftp_user_get', {'primary_id': {}})

  with open(args.ispconfig_config_backup, 'w') as outfile:
      json.dump(backup_data, outfile, indent = 1)

##### RESTORE
if args.restore_backup.lower() in ['1', 'true']:
  print('restoring')
  with open(args.ispconfig_config_backup) as json_file:
    restore_data = json.load(json_file)
    
  url = dst_url
  session_id = requests.post(url + 'login', json={'username' : args.dst_username, 'password' : args.dst_password}, verify=False).json()['response']

  key_list = ['contact_name', 'username', 'email', 'web_php_options', 'ssh_chroot', 'limit_cron_type']


  ### CLIENTS ### 
  print('restoring clients')
  for client in restore_data['clients']:
    ## add_client
    tmp = { key: value for key, value in client.items() } #if key in key_list}
    params = {}
    if 'reseller_id' not in tmp:
      params['reseller_id'] = 0
    if 'language' not in tmp or tmp['language'] == '':
      tmp['language'] = 'en'
    for k,v in tmp.items():
      params[k] = v
    r = get_command('client_add', {'params' : params} )  

  ### DOMAINS
  print('restoring domains')
  for domain in restore_data['domains']:

    tmp = { key: value for key, value in domain.items() } #if key in key_list}
    params = {}
    if 'reseller_id' not in tmp:
      params['reseller_id'] = 0
    for k,v in tmp.items():
        params[k] = v
    r = get_command('mail_domain_add', {'params' : params} )


  ### MAILBOXES  
  email_mailbox_defaults = { 'purge_trash_days' : 0,
    'purge_junk_days' : 0}
  print('restoring email boxes')
  for email_mailbox in restore_data['email_mailboxes']:  
      tmp = { key: value for key, value in email_mailbox.items() } #if key in key_list}
      params = {}
      if 'reseller_id' not in tmp:
        params['reseller_id'] = 0
      for k,v in tmp.items():
        params[k] = v
      for k,v in email_mailbox_defaults.items():
        if k not in params:
          params[k] = v
      r = get_command('mail_user_add', {'params' : params} )

  ### MAIL FORWARDS ALIASSES CATCHALLS
  print('restoring forwards, aliasses and catchalls')
  for item in restore_data['mail_types']: 
      tmp = { key: value for key, value in item.items() } #if key in key_list}
      params = {}
      if 'reseller_id' not in tmp:
        params['reseller_id'] = 0
      for k,v in tmp.items():
        params[k] = v
      # alias aliasdomain catchall forward
      commands = { 'catchall' : 'mail_catchall_add',
                   'alias' : 'mail_alias_add',
                   'forward' : 'mail_forward_add',
                   'aliasdomain' : 'mail_aliasdomain_add'
                  }
      
      if tmp['type'] in commands.keys():
        r = get_command(commands[tmp['type']], {'params' : params} )
    

  ### WEBSITES
  print('restoring websites')
  for item in restore_data['sites_web']: 
      tmp = { key: value for key, value in item.items() } #if key in key_list}
      params = {}
      if 'reseller_id' not in tmp:
        params['reseller_id'] = 0
      for k,v in tmp.items():
        params[k] = v
      # vhost alias subdomain
      commands = { 'subdomain' : 'sites_web_subdomain_add',
                   'vhost' : 'sites_web_domain_add',
                   'alias' : 'sites_web_aliasdomain_add'
                  }
      
      if tmp['type'] in commands.keys():
        r = get_command(commands[tmp['type']], {'params' : params} )

  #### FTP USERS
  #sites_ftp_user_resets = {'uid': '', 'gid': '', 'dir': ''}
  #for item in restore_data['sites_ftp_user']: 
      #tmp = { key: value for key, value in item.items() } #if key in key_list}
      #params = {}
      #if 'reseller_id' not in tmp:
        #params['reseller_id'] = 0
      #for k,v in tmp.items():
        #params[k] = v
      #for k,v in sites_ftp_user_resets.items():
        #if k in params.keys():
          #del params[k] 
        
      #r = get_command('sites_ftp_user_add', {'params' : params} )
