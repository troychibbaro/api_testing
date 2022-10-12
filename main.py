import datetime
from fastapi import FastAPI, Request
from deta import Deta
from typing import Union
from fastapi.templating import Jinja2Templates
from flask import jsonify
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()
deta = Deta()
db = deta.Base("geodata_db")
message_db = deta.Base("message_db")


#app.mount("/static", StaticFiles(directory="static", html=True), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("splash/login.html", {"request": request})


"""
Geolocation Data
"""

class GeoDict(BaseModel):
    device: str
    lat: float
    long: float
    task: str
    uid: str


@app.get("/geo/{device}-logs")
async def device_logs(device: str, latest: Union[bool, None] = None):
    logs = db.fetch({"device": device})
    if latest and logs.items:
        return db.fetch(logs.last).items
    return logs.items if logs.items else jsonify({"Error": "Entry not found"}, 404)


@app.get("/geo/{device}-logs/siri/")
async def device_logs_siri(device: str):
    logs = db.fetch({"device": device})
    if logs.items:
        i = len(logs.items) - 1
        latest = logs.items[i]
        lat = latest['lat']
        long = latest['long']
        task = latest['task']
        return {"task": task, "long": long, "lat": lat}


@app.post("/geo/report-geo/")
async def report_geographic_data(data: GeoDict):
    conv = data.dict()
    db.put(conv, key=str(datetime.today()))
    return conv


"""Messages"""


class Message(BaseModel):
    sender: str
    recipient: str
    message: str
    expires_min: int


@app.post("/mes/issue-message")
async def issue_message(mes: Message):
    exp = mes.expires_min
    d = mes.dict()
    d.pop('expires_min')
    message_db.put(d, key=str(datetime.today()), expire_in=exp*60)
    return {"Message": "Your message has been sent"}


@app.get("/mes/get-last-message-{uid}")
async def get_last_message(uid: str):
    logs = message_db.fetch({"recipient": uid})
    if logs.items:
        i = len(logs.items) - 1
        latest = logs.items[i]
        return latest
