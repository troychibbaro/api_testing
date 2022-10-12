from fastapi import FastAPI, BackgroundTasks
import pandas as pd
import datetime
from fastapi import FastAPI, Request
from deta import Deta
from typing import Union
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from flask import Flask, request, jsonify

app = FastAPI()
deta = Deta()
db = deta.Base("geodata_db")

#app.mount("/static", StaticFiles(directory="static", html=True), name="static")
templates = Jinja2Templates(directory="templates")



@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("splash/login.html", {"request": request})


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


def handle_visit(visitor):
    df = pd.read_csv("data/login_history/visits.csv")
    df.loc[len(df.index)] = (visitor, datetime.datetime.today())
    df.to_csv("data/login_history/visits.csv", index=False)


@app.get("/log-visit/{visitor}")
async def log_visit(visitor: str, tasks: BackgroundTasks):
    tasks.add_task(handle_visit, visitor)
    return {'message': 'your visit has been logged'}


@app.get("/get-visit-data")
async def get_visit_data():
    return pd.read_csv("data/login_history/visits.csv").to_json()


@app.get("/report-geo/{userId}/{lat}/{long}/{device}/{task}")
async def report_geographic_data(userId: str, lat: str, long: str, device: str, task: str):
    db.put({"userId": userId, "lat": lat, "long": long, "device": device, "task": task})
    return {"message": "geo data logged"}


@app.get("/report-geo/{userId}/{lat}/{long}/{device}/{task}/{expires}/{exp_time}")
async def report_geographic_data(userId: str, lat: str, long: str, device: str, task: str, expires: Union[bool, None] = None, exp_time: Union[int, None] = None):
    db.put({"userId": userId, "lat": lat, "long": long, "device": device, "task": task}, expire_in=exp_time)
    return {"message": f"geo data logged and will expire in {exp_time/60:.2f} minutes"}


@app.get("/geo/watch-logs")
async def watch_logs():
    logs = db.fetch({"device": "Watch"})
    return logs if logs else jsonify({"Error": "Not found"}, 404)


@app.get("/dbtest")
async def db_test():
    db.put({"key": "userId", "lat": "lat", "long": "long", "device": "device"})
    return {"message": "Successfully inserted to DB"}

@app.get("/login")
async def login(username: str, password: str, request: Request):
    df = pd.read_csv("data/credentials/users.csv", index_col="uname")
    print(df)
    if username in df.index:
        if df.loc[username]['pword'] == password:
            return RedirectResponse(f"/log-visit/{username}")
    return templates.TemplateResponse("login-process/login-denied.html", {"request": request})
