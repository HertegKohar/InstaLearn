from InstaData import Instabot
if __name__=="__main__":
	bot=Instabot.load_bot()
	bot.monitor_users()