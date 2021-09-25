from pathlib import Path
from typing import Set
from datetime import datetime
from dataclasses import dataclass
from rich.progress import track
from rich import print
import csv
import requests

lat = 47.350
lon = 8.100

rssiFilePath = Path("/Users/eliabieri/Downloads/rssi.csv")

appId = "262b0bd7ac5cf100bd4198648434b211"

days: Set[datetime] = set()

@dataclass
class Record:
    day: datetime
    temp: float
    rain3h: float
    weatherCategory: str


with Path(rssiFilePath).open(newline='') as f:
    lines = f.readlines()[1:1000]
    reader = csv.reader(lines)
    for row in track(reader, "Parsing dates", total=len(lines)):
        t = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
        day = datetime(year=t.year, month=t.month, day=t.day)
        days.add(day)

print(f"Found {len(days)} days")

data = []

for day in track(days, "Downloading data"):
    try:
        resp = requests.get(f"http://history.openweathermap.org/data/2.5/history/city?lat={lat}&lon={lon}&type=hour&start={12}&appid={appId}").json()
        print(resp)
        data.append(
            Record(day=day,
            rain3h=resp["weather"]["rain.3h"],
            temp=resp["list"]["main"]["main.temp"],
            weatherCategory=resp["weather"]["weather.main"]
            )
        )
    except Exception as e:
        print(e)

print(data)