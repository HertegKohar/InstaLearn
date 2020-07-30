import mysql.connector
import pandas as pd
from mysql.connector.errors import IntegrityError
import os

#Have to use .commit on database connection to save changes made in script
#Create a connection instance in order to communicate with the database
def connect_db():
	db_connection=mysql.connector.connect(
        host="localhost",
        user=os.environ.get('DB_USER'),
        passwd=os.environ.get('DB_PASS'),
        auth_plugin='mysql_native_password',
        database='instabase')
	return db_connection

#Insert data into the database given the processed data
def insert_db(data):
	connection=connect_db()
	cursor=connection.cursor()
	add_info=("INSERT INTO insta_train "
               "(username, posts, followers, following, private, bio_tag, external_url, verified) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
	for info in data:
		try:
			cursor.execute(add_info,info)
		except IntegrityError:
			cursor.execute(""" UPDATE insta_train SET posts={d[1]}, followers={d[2]}, following={d[3]}, private={d[4]}, 
				bio_tag={d[5]}, external_url={d[6]}, verified={d[7]} WHERE username='{d[0]}'""".format(d=info))
		finally:
			connection.commit()
	cursor.close()
	connection.close()

#Return the number of rows in the database
def size():
	connection=connect_db()
	cursor=connection.cursor()
	cursor.execute('SELECT COUNT(*) FROM insta_train')
	for output in cursor:
		rows=output[0]
	cursor.close()
	connection.close()
	return rows

#Search the data base and show the results of the row or return a row of unavailable columns
def search_db(users):
	connection=connect_db()
	cursor=connection.cursor()
	pd.set_option('display.max_columns', None)
	df=pd.DataFrame(columns=['User','Posts','Followers','Following','Private','Bio_Tag','External_Url','Verified'])
	for user in users:
		cursor.execute("SELECT * FROM insta_train WHERE username='{:s}'".format(user))
		s=None
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

#Quert and return True or False to whether the user in the in the database
def query_db(users):
	connection=connect_db()
	cursor=connection.cursor()
	df=pd.DataFrame(columns=['User','Found'])
	for user in users:
		cursor.execute("SELECT * FROM insta_train WHERE username='{:s}'".format(user))
		s=None
		for output in cursor:
			s=output
		if s:
			df=df.append({'User':user,'Found':True},ignore_index=True)
		else:
			df=df.append({'User':user,'Found':False},ignore_index=True)
	cursor.close()
	connection.close()
	return df
