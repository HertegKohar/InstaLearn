import sys
import os
os.chdir('..')
sys.path.append(os.getcwd())
os.chdir("InstaLearnApp")
from InstaLearnPackage import bot
print(dir(bot))