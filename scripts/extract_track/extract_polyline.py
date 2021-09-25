from pathlib import Path
from dataclasses import dataclass
from typing import List
import csv

@dataclass
class Coordinate:
    lat: float
    lon: float

rssiFilePath = Path("/Users/eliabieri/Downloads/rssi.csv")
outFilePath = Path("/Users/eliabieri/Downloads/polyline.dart")

coordinates: List[Coordinate] = []
with Path(rssiFilePath).open(newline='') as f:
    reader = csv.reader(f.readlines()[21383:25395])
    for row in reader:
        lat = row[6]
        lon = row[7]
        if lat is not None and lon is not None:
            print("added coordinate")
            coordinates.append(Coordinate(
                lat=float(lat),
                lon=float(lon)
            ))
with Path(outFilePath).open("w") as f:
    f.write("import 'package:latlong2/latlong.dart';\nfinal polylineTrack = [")
    for coord in coordinates:
        f.write(f"LatLng({coord.lat}, {coord.lon}),\n")
    f.write("];")