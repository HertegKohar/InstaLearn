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


def search_db(users):
	connection=connect_db()
	cursor=connection.cursor()
	pd.set_option('display.max_columns', None)
	df=pd.DataFrame(columns=['User','Posts','Followers','Following','Private','External_Url','Verified'])
	rows=''
	for user in users:
		cursor.execute("SELECT * FROM insta_train WHERE username='{:s}'".format(user))
		for output in cursor:
			s=str(output)
		try:
			s=s[1:-1]
			s=s.replace("'",'')
			s=s.replace(" ","")
			s=s.split(',')
			for i in range(4,7):
				s[i]=str(bool(int(s[i])))
			df_temp={'User':s[0],'Posts':s[1],'Followers':s[2],'Following':s[3],'Private':s[4],\
					'External_Url':s[5],'Verified':s[6]}
			df=df.append(df_temp,ignore_index=True)
		except:
			df=df.append({'User':user},ignore_index=True)
	cursor.close()
	connection.close()

	return df
