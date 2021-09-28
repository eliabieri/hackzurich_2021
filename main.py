from lib import constants
from lib.analysis import DataAnalyzer
from fastapi import FastAPI, Response, File, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from rich import print
import threading
import json

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

threading.Thread(target=DataAnalyzer.analyzeData).start()


def appendCsvData(csvFile: Path, data: bytes) -> None:
    with csvFile.open("w") as f:
        lines = data.decode('utf-8').splitlines()
        f.write("\n")
        f.writelines(f'{s}\n' for s in lines)

@app.get("/anomalies")
async def anomalies(response: Response) -> None:
    try:
        return json.loads(constants.ANOMALIES_FILE.open().read())
    except Exception as e:
        print(e)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

@app.post("/data")
async def data(
    response: Response,
    velocities: UploadFile = File(...),
    disruptions: UploadFile = File(...),
    rssi: UploadFile = File(...)):
    appendCsvData(constants.VELOCITY_FILE, await velocities.read())
    appendCsvData(constants.DISRUPTIONS_FILE, await disruptions.read())
    appendCsvData(constants.RSSI_FILE, await rssi.read())
    threading.Thread(target=DataAnalyzer.analyzeData).start()
    response.status_code = status.HTTP_200_OK