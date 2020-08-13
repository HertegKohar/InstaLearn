import os
import pickle

from fastapi import BackgroundTasks, Depends, FastAPI, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from crontab import CronTab
import models
from database import SessionLocal, engine
from models import Account, User

# Create a FastAPI instance
app = FastAPI()

models.Base.metadata.create_all(bind=engine)


class SignIn(BaseModel):
    username: str
    password: str


class CreateUser(BaseModel):
    username: str
    password: str


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


templates = Jinja2Templates(directory="templates")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.post("/add_user")
async def add_user(
    create_user: CreateUser,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user = User()
    user.username = create_user.username
    user.password = create_user.password
    try:
        db.add(user)
        db.commit()
        context = {"code": "success", "message": "user created"}
    except IntegrityError:
        context = {"code": "failed", "message": "username is already taken"}
    return context


def create_cronjob():
    with CronTab(user=os.environ.get("user")) as cron:
        job = cron.new(command="python3 cronjob.py", comment="Scrape")
        job.minute.every(1)


def get_status(context):
    with open("bot.pickle", "rb") as fv:
        bot = pickle.load(fv)
    running = False
    cron = CronTab(user=os.environ.get("user"))
    for _ in cron:
        running = True
    d = {
        "cooldown": str(bot.cooldown),
        "date_stamp": str(bot.date_stamp),
        "current_user": bot.users.peek(),
        "running": str(running),
    }
    context.update(d)
    return context


def stop_cronjob():
    with CronTab(user=os.environ.get("user")) as cron:
        cron.remove_all(comment="Scrape")


def start_up():
    stop_cronjob()
    with open("bot.pickle", "rb") as fv:
        bot = pickle.load(fv)
    bot.add_users()
    create_cronjob()


@app.post("/run")
async def run_cron(
    signin_request: SignIn,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user = db.query(User)
    user = user.filter(User.username == signin_request.username).filter(
        User.password == signin_request.password
    )
    user = user.all()
    if user:
        background_tasks.add_task(start_up)
        return {"code": "success"}
    return {"code": "failed"}


@app.post("/status")
async def status(
    signin_request: SignIn,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user = db.query(User)
    user = user.filter(User.username == signin_request.username).filter(
        User.password == signin_request.password
    )
    user = user.all()
    if user:
        return get_status({"code": "success"})

    return {"code": "failed", "message": "incorrect username or password"}


@app.post("/stop")
async def stop_cron(
    signin_request: SignIn,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user = db.query(User)
    user = user.filter(User.username == signin_request.username).filter(
        User.password == signin_request.password
    )
    user = user.all()
    if user:
        background_tasks.add_task(stop_cronjob)
        return {"code": "success"}
    return {"code": "failed"}
