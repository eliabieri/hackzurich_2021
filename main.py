from lib import constants
from lib.analysis import DataAnalyzer
from fastapi import FastAPI, Response, File, UploadFile, status
from pathlib import Path
from rich import print
import threading
import json

threading.Thread(target=DataAnalyzer.analyzeData).start()
app = FastAPI()

def appendCsvData(csvFile: Path, data: bytes) -> None:
    with csvFile.open("a") as f:
        lines = data.decode('utf-8').splitlines()[1:]
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