# Imports
import instaloader
import logging
from Instabase import *
from instaloader import Profile
from instaloader.exceptions import *
from random import choice
import os
from notify_run import Notify
import sys
import pickle
from Stack_Linked import Stack
from datetime import datetime
import traceback
from pytz import timezone
import concurrent.futures
import time

class Instabot:
	#Initialize basic logger
	logging.basicConfig(filename='logging.txt',filemode='w',format='%(levelname)s %(asctime)s - %(message)s',\
		 	level=logging.DEBUG)
	LOGGER=logging.getLogger()
	#Set the timezone and intialize notification to send messages during execution
	EST=timezone('Canada/Eastern')
	NOTIFICATION=Notify()

	def __init__(self,username=os.environ.get('IG_USER'),password=os.environ.get('IG_PASS')):
		#Create an Instaloader instance
		self.I_session=instaloader.Instaloader(max_connection_attempts=1)
		self.I_session.login(username,password)
		#Set the date stamp and cooldown
		#self.date_stamp=self.set_date_user(self.profile)
		self.cooldown=False

	#Time wrapper to get the execution time of a function
	def timer(func):
		def wrapper(*args,**kwargs):
			start_time=time.time()
			result=func(*args,**kwargs)
			exec_time=time.time()-start_time
			Instabot.LOGGER.debug('{} took {} seconds to execute'.format(func.__name__,exec_time))
			Instabot.NOTIFICATION.send('{} took {} seconds to execute'.format(func.__name__,exec_time))
			return result
		return wrapper

	#The user based function which invokes a recursive function call
	def get_posts(self):
		self._insert_posts_aux(self.I_session.get_feed_posts())
		if not self.posts.is_empty():
			self.date_stamp=self.posts.peek().date_utc

	def _insert_posts_aux(self,posts):
		"""
		Posts come in a generator so to insert them into the stack where the most recent is on the top
		need to insert recursively
		Use the date stamp as a comparison so the same post is not processed if it has been seen in a previous run
		"""
		try:
			post=next(posts)
			if post.date_utc!=self.date_stamp:
				self._insert_posts_aux(posts)
				self.posts.push(post)
		except StopIteration:
			return
	#Reset cooldown
	def reset_cooldown(self):
		self.cooldown= not self.cooldown

	#Find the most recent post and take it's date
	def set_date_stamp(self):
		self.date_stamp=next(self.I_session.get_feed_posts()).date_utc

	#Used to reset after a 429 
	def reset(self):
		self.reset_cooldown()
		self.set_date_stamp()

	#Load the bot from a pickle file 
	@staticmethod
	def load_bot():
		with open('bot.pickle','rb') as pickle_in:
			bot=pickle.load(pickle_in)
		Instabot.LOGGER.debug('Loaded Bot')
		return bot

	#Save the bot to a pickle file
	def save_bot(self):
		with open('bot.pickle','wb') as pickle_out:
			
			pickle.dump(self,pickle_out,protocol=pickle.HIGHEST_PROTOCOL)

		Instabot.LOGGER.debug('Exported to pickle file')

	#Calculate the file size of the csv in MegaBytes
	def file_size(self):
		file_stats=os.stat('InstaData.csv')
		size=file_stats.st_size / (1024 * 1024)
		return size

	def set_date_user(self,profile):
		date_stamp=next(profile.get_posts()).date_utc
		Instabot.LOGGER.debug('New Date Stamp: {}'.format(date_stamp))
		return date_stamp

	def get_profile(self,user):
		return Profile.from_username(self.I_session.context,user)

	def monitor_user(self,user):
		profile=self.get_profile(user)
		post=next(profile.get_posts())
		try:
			if post.date_utc>self.date_stamp:
				Instabot.NOTIFICATION.send('New Post')
				Instabot.LOGGER.debug('New Post Found')
				self.date_stamp=post.date_utc
				self.commenters(post.get_comments())
				self.save_bot()

		#If the post is unavailable send a notification and save the bot
		except QueryReturnedNotFoundException as err:
			Instabot.NOTIFICATION.send('404 Error Code')
			Instabot.LOGGER.warning('{}'.format(err))

		#If too many requests has been sent reset cooldown and save
		except ConnectionException as err:
			Instabot.NOTIFICATION.send("Can't get info on post need to cool down, {}".format(datetime.now(Instabot.EST)))
			Instabot.LOGGER.warning("{}".format(err))
			sys.exit()
		#Except an unexpected error and exit the program
		except Exception as err:
			Instabot.NOTIFICATION.send(traceback.format_exc(), datetime.now(Instabot.EST))
			Instabot.LOGGER.error(traceback.format_exc())
			sys.exit()

	@timer
	def get_post_comments(self):
		#Pop a post off the stack and extract the comments
		post=self.posts.pop()
		self.commenters(post.get_comments())
		Instabot.NOTIFICATION.send('InstaData.csv Size: {} MB'.format(self.file_size()))
		Instabot.NOTIFICATION.send('Finished round of data collection')

	def server_task(self):
		#Send a notification for when data collection is commencing
		Instabot.NOTIFICATION.send('Starting Data Collection, {}'.format(datetime.now(Instabot.EST)))
		if not self.cooldown:
			try:
				if not self.posts.is_empty():
					self.get_post_comments()
					self.get_posts()
				else:
					self.get_posts()
				self.save_bot()
				
			#If the post is unavailable send a notification and save the bot
			except QueryReturnedNotFoundException as err:
				Instabot.NOTIFICATION.send('404 Error Code')
				Instabot.LOGGER.warning('{}'.format(err))
				self.save_bot()

			#If too many requests has been sent reset cooldown and save
			except ConnectionException as err:
				Instabot.NOTIFICATION.send("Can't get info on post need to cool down, {}".format(datetime.now(Instabot.EST)))
				Instabot.LOGGER.warning("{}".format(err))
				self.reset_cooldown()
				self.save_bot()

			#Except an unexpected error and exit the program
			except Exception as err:
				Instabot.NOTIFICATION.send(traceback.format_exc(), datetime.now(Instabot.EST))
				Instabot.LOGGER.error(traceback.format_exc())
				sys.exit()
		else:
			Instabot.LOGGER.warning('Cooldown previously activated')
			Instabot.NOTIFICATION.send('Cooldown previously activated, {}'.format(datetime.now(Instabot.EST)))
		
	
	def commenters(self,comments,limit=20):
		"""
		Create a ThreadPoolExecutor instance in order to create seperate request for each user's information
		Pass the extract_data function into the executor and loop through the results 
		Take the processed informationa and write it into the csv
		"""
		with concurrent.futures.ThreadPoolExecutor() as executor:
			shared_data_list=[]
			try:
				for _ in range(limit):
					shared_data_list.append(executor.submit(self.extract_data,next(comments).owner))
			except StopIteration:
				Instabot.LOGGER.debug("End of comment iterator")
			finally:
				with open('InstaData.csv','a') as fv:
					for shared_data in concurrent.futures.as_completed(shared_data_list):
						try:
							info=",".join(shared_data.result())
							fv.write(info+'\n')
							Instabot.LOGGER.debug('Wrote user info to file')
						except ProfileNotExistsException:
							Instabot.LOGGER.debug('Profile not available')

	#Helper method to clean process data
	def extract_data(self,profile):
		info=(profile.username,
			str(profile.mediacount),
			str(profile.followers),
			str(profile.followees),
			str(int(profile.is_private)),
			str(int('@' in str(profile.biography.encode('utf-8')))),
			str(int(profile.external_url is not None)),
			str(int(profile.is_verified))
				)
		return info


	def export_to_file(self,filename,shared_data_list):
		with open(filename,'a') as fv:
			for shared_data in shared_data_list:
				info=str(shared_data)[1:-1].replace("'","")
				info=info.replace(" ","")
				fv.write(info+'\n')
		Instabot.NOTIFICATION.send('Exported commenters to file, {}'.format(Instabot.EST))


	def extract_data_i(self,comments,limit=20):
		for _ in range(limit):
			try:
				profile=next(comments).owner
				info=(profile.username,
					profile.mediacount,
					profile.followers,
					profile.followees,
					int(profile.is_private),
					int('@' in str(profile.biography.encode('utf-8'))),
					int(profile.external_url is not None),
					int(profile.is_verified)
						)
				yield info
				Instabot.LOGGER.debug('Gathered Info on {}'.format(profile.username))
			except StopIteration:
				Instabot.LOGGER.debug('End of the iterator')
				raise StopIteration
			except ProfileNotExistsException:
				Instabot.LOGGER.debug('Profile not available')

	

	def collect_file_data(self,filename):
		with open(filename,'r') as fv:
			fv.seek(0)
			h_map={}
			shared_data_list=[]
			for line in fv:
				info=line.split(',')
				if info[0] not in h_map:
					shared_data_list.append(tuple(info))
					h_map[info [0]]=None
		insert_db(shared_data_list)
		print(size())

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
					h_map[user]=None

		shared_data_list=self.extract_data(users)
		insert_db(shared_data_list)


	def similar_users(self,user):
		try:
			profile=Profile.from_username(self.I_session.context,user)
		except ConnectionException:
				Instabot.LOGGER.warning('Too many requests need to cool down')
				Instabot.NOTIFICATION.send('Too many requests need to cool down, closing program')
				sys.exit()
		profiles=profile.get_similar_accounts()
		shared_data_list=self.extract_data_i(profiles)
		insert_db(shared_data_list)
		return users		

	def show_users_data(self,users):
		h_map={}
		i=0
		while i<len(users):
			if users[i] in h_map:
				users.pop(i)
			else:
				h_map[users[i]]=None
				i+=1

		print(search_db(users))

	#Query the database to see if a user is within it
	def query(self,users):
		print(query_db(users))


	def show_users_data_file(self,filename):
	    with open(filename,'r') as fv:
	        fv.seek(0)
	        h_map={}
	        users=[]
	        for line in fv:
	            user=line.strip()
	            if user not in h_map:
	                users.append(user)
	                h_map[user]=None
	    print(search_db(users))