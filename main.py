from fastapi import FastAPI, BackgroundTasks
import pandas as pd
import datetime
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

#app.mount("/static", StaticFiles(directory="static", html=True), name="static")
#templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root(request: Request):
    return {"message": "hello api"}
    #return templates.TemplateResponse("splash/login.html", {"request": request})


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


"""@app.get("/login")
async def login(username: str, password: str, request: Request):
    df = pd.read_csv("data/credentials/users.csv", index_col="uname")
    print(df)
    if username in df.index:
        if df.loc[username]['pword'] == password:
            return RedirectResponse(f"/log-visit/{username}")
    return templates.TemplateResponse("login-process/login-denied.html", {"request": request})
"""
