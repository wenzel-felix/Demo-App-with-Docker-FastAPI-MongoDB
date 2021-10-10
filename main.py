import requests
from fastapi import FastAPI
from pymongo import MongoClient
import certifi
from enum import Enum
import pandas as pd
from starlette.responses import FileResponse
from starlette.background import BackgroundTasks
import os
import json

app = FastAPI()
client = MongoClient(json.load(open("config.json"))["mongoURL"],
                     ssl_ca_certs=certifi.where())
db = client.testdb
collection = db.testcollection


class BreweryType(str, Enum):
    micro = "micro"
    large = "large"
    brewpub = "brewpub"
    closed = "closed"
    proprietor = "proprietor"
    contract = "contract"
    regional = "regional"
    planning = "planning"
    nano = "nano"
    taproom = "taproom"
    bar = "bar"


class Files(str, Enum):
    xlsx = "xlsx"
    csv = "csv"
    xml = "xml"
    html = "html"


@app.on_event("startup")
async def startup_event():
    collection.remove({})
    for page in range(1, 41):
        data = requests.get(f"https://api.openbrewerydb.org/breweries?page={page}").json()
        collection.insert_many(data)


@app.get("/random_brewery")
async def get_random_brewery(items: int):
    if items > 10:
        items = 10
    result = []
    data = collection.aggregate([{"$sample": {"size": items}}])
    for i in data:
        del i["_id"]
        result.append(i)
    return result


@app.get("/{brewery_type}/random_brewery")
async def get_random_brewery_by_type(items: int, brewery_type: BreweryType):
    if items > 10:
        items = 10

    result = []
    data = collection.aggregate([
        {"$match": {"brewery_type": brewery_type.value}},
        {"$sample": {"size": items}}])
    for i in data:
        del i["_id"]
        result.append(i)

    return result


def remove_file(path: str) -> None:
    os.unlink(path)


@app.get("/breweries/{file_type}")
async def files(file_type: Files, background_tasks: BackgroundTasks):
    data = list(collection.find({}))
    df = pd.DataFrame.from_dict(data)

    if file_type.value == Files.xlsx.value:
        df.to_excel("datafiles/test.xlsx")
        background_tasks.add_task(remove_file, "datafiles/test.xlsx")
    elif file_type.value == Files.xml.value:
        df.to_xml("datafiles/test.xml")
        background_tasks.add_task(remove_file, "datafiles/test.xml")
    elif file_type.value == Files.csv.value:
        df.to_csv("datafiles/test.csv")
        background_tasks.add_task(remove_file, "datafiles/test.csv")
    elif file_type.value == Files.html.value:
        df.to_html("datafiles/test.html")
        background_tasks.add_task(remove_file, "datafiles/test.html")

    return FileResponse(path=f"./datafiles/test.{file_type.value}",
                        filename=f"test.{file_type.value}")
    # media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
