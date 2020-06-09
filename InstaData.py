# Imports
import instaloader
import logging
from Instabase import *
from instaloader import Profile
from instaloader.exceptions import ProfileNotExistsException,ConnectionException
from random import choice
import os
from notify_run import Notify
import sys
import pickle
from Stack_Linked import Stack
from datetime import datetime

class Instabot:
	logging.basicConfig(filename='logging.txt',filemode='w',format='%(levelname)s %(asctime)s - %(message)s',\
		 	level=logging.DEBUG)
	LOGGER=logging.getLogger()

	def __init__(self,username=os.environ.get('IG_USER'),password=os.environ.get('IG_PASS')):
		self.username=username
		self.password=password
		self.I_session=instaloader.Instaloader(max_connection_attempts=1)
		self.I_session.login(username,password)
		self.posts=Stack()
		self.notification=Notify()
		today=datetime.today()
		self.date_stamp=datetime(today.year,today.month,today.day,0,0,0)

	def get_posts(self):
		self._insert_posts_aux(self.I_session.get_feed_posts())

	def _insert_posts_aux(self,posts):
		try:
			post=next(posts)
			if post.date_utc>self.date_stamp:
				self._insert_posts_aux(posts)
				self.posts.push(post)
				self.date_stamp=post.date_utc
		except StopIteration:
			return

	@staticmethod
	def load_bot():
		with open('bot.pickle','rb') as pickle_in:
			bot=pickle.load(pickle_in)
		Instabot.LOGGER.debug('Loaded Bot')
		return bot

	def save_bot(self):
		with open('bot.pickle','wb') as pickle_out:
			pickle.dump(self,pickle_out)
		Instabot.LOGGER.debug('Exported to pickle file')

	def file_size(self):
		file_stats=os.stat('InstaData.csv')
		size=file_stats.st_size / (1024 * 1024)
		return size
	
	def server_task(self):
		self.notification.send('Starting Data Collection')
		if self.file_size()<1:
			try:
				data=self.random_creator()
				self.export_to_file('InstaData.csv',data)
				self.notification.send('InstaData.csv Size: {} MB'.format(self.file_size()))
				self.notification.send('Finished round of data collection')
			except:
				Instabot.LOGGER.critical('Unable to run')
				self.notification.send('Exception caught unable to run check log')
				sys.exit()
		else:
			Instabot.LOGGER.warning('File size>= 1 MB')
			self.notification.send('File size>= 1 MB')
			sys.exit()

	def extract_data(self,users):
		shared_data_list=[]
		for user in users:
			try:
				profile=Profile.from_username(self.I_session.context,user)
				info=(
					user,
					profile.mediacount,
					profile.followers,
					profile.followees,
					int(profile.is_private),
					int('@' in str(profile.biography.encode('utf-8'))),
					int(profile.external_url is not None),
					int(profile.is_verified)
					)
				shared_data_list.append(info)
			except ProfileNotExistsException:
				Instabot.LOGGER.debug('Unable to find: {}'.format(user))
				continue
			except ConnectionException:
				Instabot.LOGGER.warning('Too many requests need to cool down')
				self.notification.send('Too many requests need to cool down, closing program')
				sys.exit()
		return shared_data_list



	def extract_data_i(self,profiles,limit=20):
		looping=True
		i=0
		shared_data_list=[]
		while i<limit and looping:
			try:
				profile=next(profiles)
				info=(profile.username,
					profile.mediacount,
					profile.followers,
					profile.followees,
					int(profile.is_private),
					int('@' in str(profile.biography.encode('utf-8'))),
					int(profile.external_url is not None),
					int(profile.is_verified)
						)
				shared_data_list.append(info)
				i+=1
				Instabot.LOGGER.debug('Gather information on {}'.format(profile.username))
			except ProfileNotExistsException:
				Instabot.LOGGER.debug('Profile not available')
			except StopIteration:
				looping=False
				Instabot.LOGGER.debug('End of iterator')
			except ConnectionException:
				Instabot.LOGGER.warning('Too many requests need to cool down')
				self.notification.send('Too many requests need to cool down, closing program')
				sys.exit()
		return shared_data_list

	def export_to_file(self,filename,shared_data_list):
		with open(filename,'a') as fv:
			for shared_data in shared_data_list:
				info=str(shared_data)[1:-1].replace("'","")
				info.replace(" ","")
				fv.write(info+'\n')
		self.notification.send('Exported commenters to file')

	def collect_file_data(self,filename):
		with open(filename,'r') as fv:
			fv.seek(0)
			shared_data_list=[]
			for line in fv:
				info=line.split(',')
				shared_data_list.append(tuple(info))
		insert_db(shared_data_list)


	def collect_users_data(self,users):
		shared_data_list=[]
		shared_data_list=self.extract_data(users)
		insert_db(shared_data_list)
			
	def collect_users_data_file(self,filename):
		with open(filename,'r') as fv:
			fv.seek(0)
			users=[]
			h_map={}
			for line in fv:
				user=line.strip()
				if user not in h_map:
					users.append(user)
					h_map[user]=0

		shared_data_list=self.extract_data(users)
		insert_db(shared_data_list)


	def similar_users(self,user):
		try:
			profile=Profile.from_username(self.I_session.context,user)
		except ConnectionException:
				Instabot.LOGGER.warning('Too many requests need to cool down')
				self.notification.send('Too many requests need to cool down, closing program')
				sys.exit()
		profiles=profile.get_similar_accounts()
		shared_data_list=self.extract_data_i(profiles)
		insert_db(shared_data_list)
		return users

	def random_creator(self):
		with open('Creators.txt','r') as fv:
			creators=[]
			for line in fv:
				creators.append(line.strip())
		creator=choice(creators)
		Instabot.LOGGER.debug('Getting Post from {}'.format(creator))
		shared_data_list=self.commenters(creator)
		return shared_data_list

	def commenters(self,user,limit=20):
		try:
			profile=Profile.from_username(self.I_session.context,user)
		except ConnectionException:
				Instabot.LOGGER.warning('Too many requests need to cool down')
				self.notification.send('Too many requests need to cool down, closing program')
				sys.exit()

		posts=profile.get_posts()
		post=next(posts)
		comments=post.get_comments()
		shared_data_list=[]
		i=0
		looping=True
		while i<limit and looping:
			try:
				profile=next(comments).owner
				info=(profile.username,
					profile.mediacount,
					profile.followers,
					profile.followees,
					int(profile.is_private),
					int('@' in str(profile.biography.encode('utf-8'))) ,
					int(profile.external_url is not None),
					int(profile.is_verified)
						)
				shared_data_list.append(info)
				i+=1
				Instabot.LOGGER.debug('Gathered Info on {}'.format(profile.username))
			except StopIteration:
				looping=False
				Instabot.LOGGER.debug('End of the iterator')
			except ProfileNotExistsException:
				Instabot.LOGGER.debug('Profile not available')
		
		return shared_data_list

	def show_users_data(self,users):
		print(search_db(users))

	def show_users_data_file(self,filename):
	    with open(filename,'r') as fv:
	        fv.seek(0)
	        h_map={}
	        users=[]
	        for line in fv:
	            user=line.strip()
	            if user not in h_map:
	                users.append(user)
	                h_map[user]=0
	    print(search_db(users))