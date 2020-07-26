from fastapi import FastAPI, Request, BackgroundTasks, Depends
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

#Create a FastAPI instance
app=FastAPI()

class AddUser(BaseModel):
	username: str

templates=Jinja2Templates(directory='templates')


@app.get('/')
def home(request: Request):
	return templates.TemplateResponse('home.html',{'request':request})

@app.post("/user")
async def add_user(request: Request, background_tasks:BackgroundTasks):
	background_tasks.add_task(test_notification)
	return {"code":"success"}

@app.post('/run')
async def run_cron(request: Request, background_tasks: BackgroundTasks):
	pass


	

