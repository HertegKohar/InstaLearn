from fastapi import FastAPI, Request, BackgroundTasks, Depends
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import sys
import os
os.chdir('..')
sys.path.append(os.getcwd())
os.chdir("InstaLearnApp")
from InstaLearnPackage import bot

#Create a FastAPI instance
app=FastAPI()

class AddUser(BaseModel):
	username: str

templates=Jinja2Templates(directory='templates')


@app.get('/')
def home(request: Request):
	return templates.TemplateResponse('home.html',{'request':request})


@app.post("/user")
def add_user(user_request, background_tasks: BackgroundTasks):
	pass
