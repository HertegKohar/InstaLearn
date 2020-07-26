import sys
import os
os.chdir('..')
sys.path.append(os.getcwd())
os.chdir("InstaLearnApp")
from InstaLearnPackage import bot
#bot.monitor_users()
for user in bot.users: print(user)
bot.save_bot()