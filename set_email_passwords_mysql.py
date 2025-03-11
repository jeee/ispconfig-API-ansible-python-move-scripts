#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser(description='Update passwords of email users in dpispconfig database')
parser.add_argument('--mysql_db', metavar='mysql_database', default='dbispconfig', type=str,
                   help='mysql database to connect to')
parser.add_argument('--mysql_server', metavar='mysql_server_address', default='localhost',
                    type=str,  help='mysql server address')
parser.add_argument('--mysql_user', metavar='mysql_user_name', default='root', type=str,   
                    help='mysql user name')
parser.add_argument('mysql_pass', metavar='mysql_user_password', type=str,
                    help='mysql user password')
parser.add_argument('mysql_email_password_file', metavar='mysql_email_password_file', default='mysql-email-passwords.txt', type=str,   
                    help='filename of file containing lines with email[tab]mysql_stored_password')
args = parser.parse_args()

data = {}

with open(args.mysql_email_password_file) as f:
   lines = f.readlines()
   for l in lines:
     email,password = l.split('\t')
     data[email] =  password.strip()
                 
print(data)


query = """UPDATE mail_user
   SET password = CASE email 
                      %s 
                      ELSE email
                      END
 WHERE email IN(%s);""" % ( '\n'.join(['WHEN \'%s\' THEN \'%s\'' % (k,v) for k,v in data.items()]) ,','.join(['\'%s\'' % v for v in data.keys()]))
 
print(query)

import pymysql

db = pymysql.connect(host=args.mysql_server, user=args.mysql_user, password=args.mysql_pass, database=args.mysql_db )

cursor = db.cursor() 

cursor.execute(query)   
db.commit()
db.close()

