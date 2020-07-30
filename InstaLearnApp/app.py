from fastapi import FastAPI, Request, BackgroundTasks, Depends
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
from crontab import CronTab

#Create a FastAPI instance
app=FastAPI()

class SignIn(BaseModel):
	username: str
	password: str

templates=Jinja2Templates(directory='templates')


@app.get('/')
def home(request: Request):
	return templates.TemplateResponse('home.html',{'request':request})

@app.get("/user")
async def add_user(request: Request, background_tasks:BackgroundTasks):
	return {"code":"success"}

def cronjob():
	with CronTab(user=os.environ.get('user')) as cron:
		job=cron.new(command='/usr/bin/python3 /home/{:s}/cronjob.py'.format(os.environ.get('user')))
		job.minute.every(1)


@app.post('/run')
async def run_cron(signin_request: SignIn, background_tasks: BackgroundTasks):
	if signin_request.username==os.environ.get('username') and signin_request.password==os.environ.get('password'):
		background_tasks.add_task(cronjob)
		return {"code":"success"}
	return {"code":"failed"}

@app.get('/status')
async def run_cron(signin_request: SignIn, background_tasks: BackgroundTasks):
	if signin_request.username==os.environ.get('username') and signin_request.password==os.environ.get('password'):
		pass
	return 







	

