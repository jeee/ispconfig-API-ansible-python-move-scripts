#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser(description='')
parser.add_argument('--mysql_db', metavar='mysql_database', default='dbispconfig', type=str,
                   help='mysql database to connect to')
parser.add_argument('--mysql_server', metavar='mysql_server_address', default='localhost',
                    type=str,  help='mysql server address')
parser.add_argument('--mysql_user', metavar='mysql_user_name', default='root', type=str,   
                    help='mysql user name')
parser.add_argument('mysql_pass', metavar='mysql_user_password', type=str,
                    help='mysql user password')

args = parser.parse_args()

import pymysql

# Open database connection
db = pymysql.connect(args.mysql_server,args.mysql_user,args.mysql_pass,args.mysql_db )

# prepare a cursor object using cursor() method
cursor = db.cursor() 

query = "Select email, password from mail_user;"
cursor.execute(query)

# Fetch all the rows in a list of lists.
results = cursor.fetchall()
for row in results:
  user_email = row[0]
  user_pass = row[1]
  print ("%s\t%s" % \
      (user_email, user_pass))

db.close()



