from lib import constants
from fastapi import FastAPI, Response, File, UploadFile, status
from pathlib import Path

app = FastAPI()

def appendCsvData(csvFile: Path, data: bytes) -> None:
    with csvFile.open("a") as f:
        lines = data.decode('utf-8').splitlines()[1:]
        print(lines)
        f.writelines(lines)

@app.get("/anomalies")
async def anomalies():
    return constants.ANOMALIES_FILE.open().read()

@app.post("/data")
async def data(
    response: Response,
    events: UploadFile = File(...),
    disruptions: UploadFile = File(...),
    rssi: UploadFile = File(...)):
    appendCsvData(constants.EVENTS_FILE, await events.read())
    appendCsvData(constants.DISRUPTIONS_FILE, await disruptions.read())
    appendCsvData(constants.RSSI_FILE, await rssi.read())
    response.status_code = status.HTTP_200_OK