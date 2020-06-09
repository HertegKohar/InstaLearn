from InstaData import Instabot
from Credentials import *
from datetime import datetime
from Stack_Linked import Stack
from datetime import datetime
if __name__ == "__main__":
	bot=Instabot.load_bot()
	today=datetime.today()
	with open('Debug.txt','w') as fv:
		for post in bot.comments:
			fv.write(str(post.pcaption.encode('utf-8'))+' '+str(post.date_local)+'\n\n')
	time_stamp=datetime(today.year,today.month,today.day,0,0,0)
	# feed=iter(bot.comments)
	# s=Stack()
	# def recurse(feed):
	# 	try:
	# 		post=next(feed)
	# 		if post.date_utc>time_stamp:
	# 			recurse(feed)
	# 			s.push(post)
	# 	except StopIteration:
	# 		return
	# recurse(feed)
	# for post in s:
	# 	print(post.date_utc,post.pcaption.encode('utf-8'))


	

	

	



	


	
	






	

	


	








	