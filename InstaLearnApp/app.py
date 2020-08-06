from fastapi import FastAPI, Request, BackgroundTasks, Depends
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
import pickle
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

def create_cronjob():
	with CronTab(user=os.environ.get('user')) as cron:
		job=cron.new(command='python3 cronjob.py',comment='Scrape')
		job.minute.every(1)

def get_status(context):
	with open('bot.pickle','rb') as fv:
		bot=pickle.load(fv)
	running=False
	cron=CronTab(user=os.environ.get('user'))
	for job in cron: running=True
	d={"cooldown":str(bot.cooldown),'date_stamp':str(bot.date_stamp),\
	'current_user':bot.users.peek(),'running':str(running)}
	context.update(d) 
	return context

def stop_cronjob():
	with CronTab(user=os.environ.get('user')) as cron: cron.remove_all(comment='Scrape')

def start_up():
	stop_cronjob()
	with open('bot.pickle','rb') as fv: bot=pickle.load(fv)
	bot.add_users()
	create_cronjob()

@app.post('/run')
async def run_cron(signin_request: SignIn, background_tasks: BackgroundTasks):
	if signin_request.username==os.environ.get('username') and signin_request.password==os.environ.get('password'):
		background_tasks.add_task(start_up)
		return {"code":"success"}
	return {"code":"failed"}

@app.post('/status')
async def status(signin_request:SignIn,background_tasks: BackgroundTasks):
	if signin_request.username==os.environ.get('username') and signin_request.password==os.environ.get('password'):
		return get_status({"code":"success"})
	return {"code":"failed"}

@app.post('/stop')
async def stop_cron(signin_request:SignIn,background_tasks: BackgroundTasks):
	if signin_request.username==os.environ.get('username') and signin_request.password==os.environ.get('password'):
		background_tasks.add_task(stop_cronjob)
		return {"code":"success"}
	return {"code":"failed"}




	

