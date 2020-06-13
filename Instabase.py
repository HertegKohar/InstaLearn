import mysql.connector
import pandas as pd
from io import StringIO
from mysql.connector.errors import InterfaceError
import os

#Have to use .commit on database connection to save changes made in script
def connect_db():
	db_connection=mysql.connector.connect(
        host="localhost",
        user=os.environ.get('DB_USER'),
        passwd=os.environ.get('DB_PASS'),
        auth_plugin='mysql_native_password',
        database='instabase')
	return db_connection

def insert_db(data):
	connection=connect_db()
	cursor=connection.cursor()
	add_info=("INSERT INTO insta_train "
               "(username, posts, followers, following, private, bio_tag, external_url, verified) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
	for info in data:
		try:
			cursor.execute(add_info,info)
			connection.commit()
		except:
			continue
	cursor.close()
	connection.close()

def size():
	connection=connect_db()
	cursor=connection.cursor()
	cursor.execute('SELECT COUNT(*) FROM insta_train')
	for output in cursor:
		print(output[0])
	cursor.close()
	connection.close()

def search_db(users):
	connection=connect_db()
	cursor=connection.cursor()
	pd.set_option('display.max_columns', None)
	df=pd.DataFrame(columns=['User','Posts','Followers','Following','Private','Bio_Tag','External_Url','Verified'])
	for user in users:
		cursor.execute("SELECT * FROM insta_train WHERE username='{:s}'".format(user))
		for output in cursor:
			s=output
		if s:
			df_temp={'User':s[0],'Posts':s[1],'Followers':s[2],'Following':s[3],'Private':bool(s[4]),\
					'Bio_Tag':bool(s[5]),'External_Url':bool(s[6]),'Verified':bool(s[7])}
			df=df.append(df_temp,ignore_index=True)
		else:
			df=df.append({'User':user},ignore_index=True)
	cursor.close()
	connection.close()
	return df